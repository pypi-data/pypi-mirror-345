from datetime import datetime, timedelta
from uuid import uuid4

import httpx
import structlog
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

User = get_user_model()

logger = structlog.get_logger(__name__)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NetworkMembership(TimestampedModel):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    network = models.ForeignKey(
        "Network", on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("network", "user"), name="unique_network_membership"
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.network} {self.role}"


class Network(TimestampedModel):
    name = models.CharField(max_length=200, unique=True)
    cidr = models.CharField(max_length=200, default="100.100.64.0/24")
    update_interval = models.IntegerField(
        default=5, help_text="Interval in seconds for host configuration updates"
    )
    members = models.ManyToManyField(
        User, through="NetworkMembership", related_name="networks"
    )

    def __str__(self):
        return self.name


class CA(TimestampedModel):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    key = models.TextField()
    cert = models.TextField()
    cert_print = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def days_until_expiry(self):
        if (
            not self.cert_print
            or "details" not in self.cert_print
            or "notAfter" not in self.cert_print["details"]
        ):
            return None

        expiry_str = self.cert_print["details"]["notAfter"]
        try:
            expiry_date = datetime.fromisoformat(expiry_str)
            days = (expiry_date - timezone.now()).days
            return max(0, days)
        except (ValueError, TypeError) as e:
            logger.error("error parsing expiry date", ca_name=self.name, error=e)
            return None


class SigningCA(TimestampedModel):
    network = models.OneToOneField(Network, on_delete=models.CASCADE)
    ca = models.ForeignKey(CA, on_delete=models.CASCADE)

    def __str__(self):
        return self.ca.name


class Group(TimestampedModel):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("network", "name"), name="unique_group_name_per_network"
            ),
        ]

    def __str__(self):
        return self.name


class GroupConfig(TimestampedModel):
    CONFIG_KEY_CHOICES = [
        ("lighthouse.dns.host", "Lighthouse DNS Host"),
        ("lighthouse.dns.port", "Lighthouse DNS Port"),
        ("lighthouse.serve_dns", "Lighthouse Serve DNS"),
    ]

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="config_overrides"
    )
    key = models.CharField(
        max_length=255,
        choices=CONFIG_KEY_CHOICES,
        help_text="Configuration property to override or add.",
    )
    value = models.TextField(
        help_text="The value to override the config property with."
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=("group", "key"), name="unique_group_config_key"),
        ]

    def __str__(self):
        return f"{self.group.name} - {self.key}"


class Rule(TimestampedModel):
    class Direction(models.TextChoices):
        INBOUND = "I", "inbound"
        OUTBOUND = "O", "outbound"

    security_group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="rules"
    )

    direction = models.CharField(
        max_length=10, choices=Direction.choices, default=Direction.INBOUND
    )

    class Protocol(models.TextChoices):
        ANY = "any", "any"
        UDP = "udp", "udp"
        TCP = "tcp", "tcp"
        ICMP = "icmp", "icmp"

    proto = models.CharField(
        max_length=4,
        choices=Protocol.choices,
        default=Protocol.ANY,
        help_text="One of any, tcp, udp, or icmp",
    )

    port = models.CharField(
        max_length=255,
        help_text=(
            "Takes 0 or any as any, a single number (e.g. 80), a range (e.g. 200-901), "
            "or fragment to match second and further fragments of fragmented packets "
            "(since there is no port available)."
        ),
        default="any",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        help_text="Can be any or a literal group name, ie default-group",
        blank=True,
        null=True,
        related_name="fw_groups",
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="fw_groupss",
        help_text=(
            "Same as group but accepts multiple values. Multiple values are AND'd together "
            "and a certificate must contain all groups to pass."
        ),
    )

    cidr = models.CharField(
        max_length=255,
        help_text="a CIDR, 0.0.0.0/0 is any. This restricts which Nebula IP addresses the rule allows.",
        blank=True,
        null=True,
    )

    local_cidr = models.CharField(
        max_length=255,
        help_text=(
            "a local CIDR, 0.0.0.0/0 is any. This restricts which destination IP addresses, "
            "when using unsafe_routes, the rule allows. If unset, the rule will allow access "
            "to the specified ports on both the node itself as well as any IP addresses it routes to."
        ),
        blank=True,
        null=True,
    )


class Host(TimestampedModel):
    class Meta:
        unique_together = (("network", "name"), ("network", "assigned_ip"))

    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    assigned_ip = models.CharField(max_length=200, blank=True, null=True)

    is_lighthouse = models.BooleanField(default=False)
    public_ip_or_hostname = models.CharField(max_length=200, blank=True, null=True)

    is_relay = models.BooleanField(default=False)
    use_relay = models.BooleanField(default=True)

    public_key = models.TextField(max_length=1000, blank=True, null=True)
    public_auth_kid = models.CharField(max_length=200, blank=True, null=True)
    public_auth_key = models.TextField(max_length=1000, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True)
    interface = models.CharField(max_length=200, default="nebula1")

    last_config_refresh = models.DateTimeField(blank=True, null=True)

    config_freeze = models.BooleanField(
        default=False,
        help_text="When true, host will not receive automatic config updates",
    )

    is_ephemeral = models.BooleanField(
        default=False,
        help_text="When true, this host will be removed if offline for over 10 minutes",
    )
    cli_version = models.CharField(
        max_length=50, blank=True, help_text="Client CLI version"
    )
    upgrade_requested = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def is_config_stale(self):
        if not self.last_config_refresh:
            return True

        stale_threshold = timezone.now() - timedelta(hours=24)
        return self.last_config_refresh < stale_threshold

    @property
    def is_cli_version_outdated(self) -> bool | str:
        if not self.cli_version:
            return "Unknown"

        latest_version = self.get_latest_cli_version
        if not latest_version:
            return "Unknown"

        return self.cli_version != latest_version

    @property
    def get_latest_cli_version(self) -> str | None:
        try:
            response = httpx.get("https://pypi.org/pypi/meshadmin/json")
            if response.status_code == 200:
                return response.json()["info"]["version"]
        except Exception:
            pass
        return None


class HostCert(TimestampedModel):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    ca = models.ForeignKey(CA, on_delete=models.CASCADE)
    cert = models.TextField(max_length=1000)
    hash = models.IntegerField(default=0)


class HostConfig(TimestampedModel):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    config = models.TextField()
    sha256 = models.CharField(max_length=200, blank=True, null=True)


class Template(TimestampedModel):
    name = models.CharField(max_length=200)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    is_lighthouse = models.BooleanField(default=False)
    is_relay = models.BooleanField(default=False)
    use_relay = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, blank=True)
    enrollment_key = models.CharField(max_length=255, default=uuid4, unique=True)

    reusable = models.BooleanField(
        default=True, help_text="When false, this key can not be used multiple times"
    )
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of peers that can enroll with this key. Null means unlimited.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key expires. Null means no expiration.",
    )
    usage_count = models.IntegerField(
        default=0, help_text="Number of times this key has been used"
    )
    ephemeral_peers = models.BooleanField(
        default=False,
        help_text="When true, peers that are offline for over 10 minutes will be removed",
    )

    def __str__(self):
        return self.name


class ConfigRollout(TimestampedModel):
    name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    target_hosts = models.ManyToManyField(Host, related_name="pending_rollouts")
    completed_hosts = models.ManyToManyField(Host, related_name="completed_rollouts")
    notes = models.TextField(blank=True)
