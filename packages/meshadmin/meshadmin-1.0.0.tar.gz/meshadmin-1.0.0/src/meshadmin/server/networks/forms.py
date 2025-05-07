import ipaddress
from datetime import timedelta

import structlog
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from meshadmin.server.networks.models import (
    CA,
    Group,
    GroupConfig,
    Host,
    Network,
    NetworkMembership,
    Rule,
    Template,
)
from meshadmin.server.networks.services import (
    create_network,
    create_network_ca,
    network_available_hosts_iterator,
)

logger = structlog.get_logger(__name__)

User = get_user_model()

RECOMMENDED_RANGES = [
    ("192.168.0.0/16", "Private network range, ideal for small networks"),
    ("172.16.0.0/12", "Private network range, good for medium networks"),
    ("10.0.0.0/8", "Private network range, suitable for large networks"),
    ("100.64.0.0/10", "Carrier-grade NAT range, recommended by Nebula docs"),
]


class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ("name", "cidr", "update_interval")
        widgets = {
            "update_interval": forms.NumberInput(attrs={"min": 5, "max": 3600}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_cidr(self):
        cidr = self.cleaned_data["cidr"]

        try:
            network = ipaddress.ip_network(cidr)
        except ValueError as e:
            raise ValidationError(f"Invalid CIDR format: {str(e)}")

        in_recommended_range = False
        for recommended_cidr, _ in RECOMMENDED_RANGES:
            if ipaddress.ip_network(cidr).subnet_of(
                ipaddress.ip_network(recommended_cidr)
            ):
                in_recommended_range = True
                break

        if not in_recommended_range:
            suggestions = []
            network_size = network.num_addresses
            for recommended_cidr, description in RECOMMENDED_RANGES:
                rec_network = ipaddress.ip_network(recommended_cidr)
                if network_size <= rec_network.num_addresses:
                    suggestions.append(f"{recommended_cidr} - {description}")

            raise ValidationError(
                f"Warning: The CIDR {cidr} is outside recommended network ranges. "
                "Consider using one of these ranges instead:\n"
                + "\n".join(f"• {suggestion}" for suggestion in suggestions)
            )

        return cidr

    def save(self, commit=True):
        logger.info("save network")
        instance = super().save(commit=False)
        if not instance.pk:
            instance = create_network(
                network_name=self.cleaned_data["name"],
                network_cidr=self.cleaned_data["cidr"],
                update_interval=self.cleaned_data["update_interval"],
                user=self.request.user,
            )
        elif commit:
            instance.save()

        self.save_m2m()
        return instance


class CAForm(forms.ModelForm):
    class Meta:
        model = CA
        fields = ("name", "network")

    def __init__(self, *args, **kwargs):
        network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)

        if network:
            self.fields.pop("network")
            self.instance.network = network

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk:
            if commit:
                instance.save()
        else:
            instance = create_network_ca(instance.name, instance.network)

        return instance


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "description")

    def __init__(self, *args, **kwargs):
        network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)

        if network:
            self.instance.network = network


class TemplateForm(forms.ModelForm):
    expiry_days = forms.IntegerField(
        required=False,
        min_value=1,
        label="Expires in (days)",
        help_text="Days until the key expires. Leave empty for no expiration.",
    )

    class Meta:
        model = Template
        fields = (
            "name",
            "network",
            "is_lighthouse",
            "is_relay",
            "use_relay",
            "groups",
            "reusable",
            "usage_limit",
            "ephemeral_peers",
        )

    def __init__(self, *args, **kwargs):
        network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.expires_at:
            days_remaining = (self.instance.expires_at - timezone.now()).days
            if days_remaining > 0:
                self.fields["expiry_days"].initial = days_remaining

        network_id = None
        if network:
            network_id = network.id
            self.fields.pop("network")
            self.instance.network = network
        elif self.instance and self.instance.pk:
            network_id = self.instance.network_id
        elif "initial" in kwargs and "network_id" in kwargs["initial"]:
            network_id = kwargs["initial"]["network_id"]

        if network_id:
            self.fields["groups"].queryset = Group.objects.filter(
                network_id=network_id
            ).all()

    def save(self, commit=True):
        instance = super().save(commit=False)

        expiry_days = self.cleaned_data.get("expiry_days")
        if expiry_days:
            instance.expires_at = timezone.now() + timedelta(days=expiry_days)
        elif "expiry_days" in self.changed_data:
            instance.expires_at = None

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = (
            "name",
            "network",
            "assigned_ip",
            "is_lighthouse",
            "is_relay",
            "use_relay",
            "groups",
            "public_ip_or_hostname",
            "public_auth_key",
            "interface",
        )

    def __init__(self, *args, **kwargs):
        network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)

        network_id = None
        if network:
            network_id = network.id
            self.fields.pop("network")
            self.instance.network = network
        elif self.instance and self.instance.pk:
            network_id = self.instance.network_id

        if network_id:
            self.fields["groups"].queryset = Group.objects.filter(
                network_id=network_id
            ).all()

            if not self.instance.pk:
                network = Network.objects.get(id=network_id)
                ipv4_iterator = network_available_hosts_iterator(network)
                self.initial["assigned_ip"] = next(ipv4_iterator)


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = (
            "direction",
            "proto",
            "port",
            "group",
            "groups",
            "cidr",
            "local_cidr",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        security_group_id = kwargs.get("initial", {}).get("security_group_id")
        if not security_group_id and kwargs.get("instance"):
            security_group_id = kwargs["instance"].security_group_id

        if security_group_id:
            security_group = get_object_or_404(Group, id=security_group_id)
            group_queryset = Group.objects.filter(network_id=security_group.network_id)
            self.fields["group"].queryset = group_queryset
            self.fields["groups"].queryset = group_queryset

    def clean(self):
        cleaned_data = super().clean()

        # Validate port format
        port = cleaned_data.get("port")
        if port and port not in ("0", "any", "fragment"):
            if "-" in port:
                try:
                    start, end = map(int, port.split("-"))
                    if not (0 <= start <= 65535 and 0 <= end <= 65535):
                        raise ValueError
                except ValueError:
                    raise ValidationError(
                        {
                            "port": "Port range must be two valid port numbers (0-65535) separated by a hyphen"
                        }
                    )
            elif not port.isdigit() or not 0 <= int(port) <= 65535:
                raise ValidationError(
                    {
                        "port": "Port must be 'any', 'fragment', or a number between 0 and 65535"
                    }
                )

        # Validate that at least one target specification exists
        group = cleaned_data.get("group")
        groups = cleaned_data.get("groups")
        cidr = cleaned_data.get("cidr")

        if not any([group, groups.exists() if groups else False, cidr]):
            raise ValidationError(
                "At least one of group, groups, or CIDR must be specified to identify "
                "which hosts the rule applies to."
            )

        # Validate CIDR format if provided
        if cidr:
            try:
                ipaddress.ip_network(cidr)
            except ValueError:
                raise ValidationError(
                    {"cidr": "Invalid CIDR format. Example: 0.0.0.0/0"}
                )

        # Validate local_cidr format if provided
        local_cidr = cleaned_data.get("local_cidr")
        if local_cidr:
            try:
                ipaddress.ip_network(local_cidr)
            except ValueError:
                raise ValidationError(
                    {"local_cidr": "Invalid CIDR format. Example: 0.0.0.0/0"}
                )

        return cleaned_data


class NetworkMembershipForm(forms.ModelForm):
    email = forms.EmailField(
        help_text="Enter the email address of the user you want to add to the network"
    )

    class Meta:
        model = NetworkMembership
        fields = ["role"]

    def __init__(self, *args, **kwargs):
        self.network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["email"].initial = self.instance.user.email
            self.fields["email"].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("No user found with this email address")
        if (
            self.network
            and NetworkMembership.objects.filter(
                network=self.network, user=user
            ).exists()
        ):
            raise ValidationError("This user is already a member of the network")
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            email = self.cleaned_data["email"]
            user = User.objects.get(email=email)
            instance.user = user
            instance.network = self.network
        if commit:
            instance.save()
        return instance


class GroupConfigForm(forms.ModelForm):
    class Meta:
        model = GroupConfig
        fields = ["key", "value"]
        widgets = {
            "value": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_value(self):
        value = self.cleaned_data["value"]
        key = self.cleaned_data.get("key")

        if not key:
            return value

        # Validate value based on the selected key
        if key == "lighthouse.interval":
            try:
                interval = int(value)
                if interval < 1:
                    raise forms.ValidationError("Interval must be a positive integer")
                return str(interval)
            except ValueError:
                raise forms.ValidationError("Interval must be a valid integer")

        elif key == "lighthouse.dns.port":
            try:
                port = int(value)
                if port < 1 or port > 65535:
                    raise forms.ValidationError("Port must be between 1 and 65535")
                return str(port)
            except ValueError:
                raise forms.ValidationError("Port must be a valid integer")

        elif key == "lighthouse.serve_dns":
            if value.lower() not in ["true", "false"]:
                raise forms.ValidationError("Value must be a boolean (true/false)")
            return value.lower()
