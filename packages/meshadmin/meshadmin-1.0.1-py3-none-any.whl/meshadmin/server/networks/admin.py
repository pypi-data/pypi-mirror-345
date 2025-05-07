import structlog
from django import forms
from django.contrib import admin

from meshadmin.server.networks.models import (
    CA,
    Group,
    GroupConfig,
    Host,
    HostCert,
    HostConfig,
    Network,
    NetworkMembership,
    Rule,
    SigningCA,
    Template,
)
from meshadmin.server.networks.services import create_network

logger = structlog.get_logger(__name__)


class CaInline(admin.StackedInline):
    model = CA
    extra = 0
    fields = ("name", "cert_print")
    readonly_fields = (
        "name",
        "cert_print",
    )


class HostInline(admin.TabularInline):
    model = Host
    extra = 0


class GroupInline(admin.TabularInline):
    model = Group
    extra = 0


class SigningCAInline(admin.StackedInline):
    model = SigningCA
    extra = 0


class TemplateInline(admin.TabularInline):
    model = Template
    extra = 0


class NetworkAdminForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ("name", "cidr")


class NetworkMembershipInline(admin.TabularInline):
    model = NetworkMembership
    extra = 0


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    form = NetworkAdminForm

    def get_inlines(self, request, obj):
        if obj:
            return [
                CaInline,
                SigningCAInline,
                HostInline,
                GroupInline,
                TemplateInline,
                NetworkMembershipInline,
            ]
        else:
            return []

    def save_model(self, request, obj: Network, form, change):
        if not change:
            create_network(obj.name, obj.cidr, request.user)
        else:
            obj.save()


class HostCertInline(admin.TabularInline):
    model = HostCert
    extra = 0


class HostConfigInline(admin.TabularInline):
    model = HostConfig
    extra = 0


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "network__name", "assigned_ip")
    list_filter = ("network",)
    inlines = [
        HostCertInline,
        HostConfigInline,
    ]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "network__name"]
    list_filter = ("network",)


class RuleInline(admin.TabularInline):
    model = Rule
    extra = 0


class GroupConfigInline(admin.TabularInline):
    model = GroupConfig
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ("network",)
    inlines = (GroupConfigInline,)
