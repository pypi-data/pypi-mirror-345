from django.urls import path

from meshadmin.server.networks import views
from meshadmin.server.networks.views import rollout

app_name = "networks"

urlpatterns = [
    path("", views.NetworkListView.as_view(), name="network-list"),
    path("network/create/", views.NetworkCreateView.as_view(), name="network-create"),
    path("network/<int:pk>/", views.NetworkDetailView.as_view(), name="network-detail"),
    path(
        "network/<int:pk>/edit/", views.NetworkUpdateView.as_view(), name="network-edit"
    ),
    path(
        "network/<int:pk>/delete/",
        views.NetworkDeleteView.as_view(),
        name="network-delete",
    ),
    path(
        "network/<int:network_id>/host/create/",
        views.HostCreateView.as_view(),
        name="network-host-create",
    ),
    path("host/<int:pk>/", views.HostDetailView.as_view(), name="host-detail"),
    path("host/<int:pk>/edit/", views.HostUpdateView.as_view(), name="host-edit"),
    path("host/<int:pk>/delete/", views.HostDeleteView.as_view(), name="host-delete"),
    path(
        "host/<int:pk>/refresh-config/<int:rollout_id>/",
        views.HostRefreshConfigView.as_view(),
        name="host-refresh-config",
    ),
    path(
        "host/<int:pk>/config", views.HostConfigView.as_view(), name="show-host-config"
    ),
    path(
        "network/<int:network_id>/template/create/",
        views.TemplateCreateView.as_view(),
        name="network-template-create",
    ),
    path(
        "template/<int:pk>/", views.TemplateDetailView.as_view(), name="template-detail"
    ),
    path(
        "template/<int:pk>/edit/",
        views.TemplateUpdateView.as_view(),
        name="template-edit",
    ),
    path(
        "template/<int:pk>/delete/",
        views.TemplateDeleteView.as_view(),
        name="template-delete",
    ),
    path(
        "network/<int:network_id>/group/create/",
        views.GroupCreateView.as_view(),
        name="network-group-create",
    ),
    path("group/<int:pk>/", views.GroupDetailView.as_view(), name="group-detail"),
    path("group/<int:pk>/edit/", views.GroupUpdateView.as_view(), name="group-edit"),
    path(
        "group/<int:pk>/delete/", views.GroupDeleteView.as_view(), name="group-delete"
    ),
    path("group/add-rule/", views.GroupAddRuleView.as_view(), name="group-add-rule"),
    path("rule/form-modal/", views.RuleFormModalView.as_view(), name="rule-form-modal"),
    path(
        "group/config-modal/",
        views.GroupConfigModalView.as_view(),
        name="group-config-modal",
    ),
    path(
        "group/add-config/",
        views.GroupAddUpdateConfigView.as_view(),
        name="group-add-config",
    ),
    path(
        "group/config/<int:pk>/delete/",
        views.GroupConfigDeleteView.as_view(),
        name="group-config-delete",
    ),
    path(
        "security-group/<int:security_group_id>/rule/create/",
        views.RuleCreateView.as_view(),
        name="security-group-rule-create",
    ),
    path(
        "network/<int:network_id>/ca/create/",
        views.CACreateView.as_view(),
        name="network-ca-create",
    ),
    path("ca/<int:pk>/", views.CADetailView.as_view(), name="ca-detail"),
    path("ca/<int:pk>/edit/", views.CAUpdateView.as_view(), name="ca-edit"),
    path("ca/<int:pk>/delete/", views.CADeleteView.as_view(), name="ca-delete"),
    path(
        "ca/<int:pk>/make-signing/",
        views.CAMakeSigningView.as_view(),
        name="ca-make-signing",
    ),
    path("rule/<int:pk>/", views.RuleDetailView.as_view(), name="rule-detail"),
    path("rule/<int:pk>/edit/", views.RuleUpdateView.as_view(), name="rule-edit"),
    path("rule/<int:pk>/delete/", views.RuleDeleteView.as_view(), name="rule-delete"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "host/<int:base_id>/diff/<int:compare_id>/",
        views.ConfigDiffView.as_view(),
        name="config-diff",
    ),
    path(
        "host/<int:pk>/upgrade/",
        views.HostUpgradeView.as_view(),
        name="host-upgrade",
    ),
    path(
        "networks/<int:network_id>/rollouts/create/",
        rollout.RolloutCreateView.as_view(),
        name="network-rollout-create",
    ),
    path(
        "rollouts/<int:pk>/",
        rollout.RolloutDetailView.as_view(),
        name="rollout-detail",
    ),
    path(
        "rollouts/<int:pk>/unfreeze/",
        rollout.UnfreezeHostConfigView.as_view(),
        name="rollout-unfreeze",
    ),
    path(
        "rollouts/<int:pk>/edit/",
        rollout.RolloutUpdateView.as_view(),
        name="rollout-edit",
    ),
    path(
        "rollouts/<int:pk>/delete/",
        rollout.RolloutDeleteView.as_view(),
        name="rollout-delete",
    ),
    path(
        "networks/<int:network_id>/members/add/",
        views.NetworkMemberAddView.as_view(),
        name="network-member-add",
    ),
    path(
        "networks/<int:network_id>/members/<int:pk>/edit/",
        views.NetworkMemberEditView.as_view(),
        name="network-member-edit",
    ),
    path(
        "networks/<int:network_id>/members/<int:pk>/delete/",
        views.NetworkMemberDeleteView.as_view(),
        name="network-member-delete",
    ),
]
