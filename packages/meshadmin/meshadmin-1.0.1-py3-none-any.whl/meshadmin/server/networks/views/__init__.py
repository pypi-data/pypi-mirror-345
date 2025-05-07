from .auth import LogoutView
from .ca import (
    CACreateView,
    CADeleteView,
    CADetailView,
    CAMakeSigningView,
    CAUpdateView,
)
from .group import (
    GroupAddRuleView,
    GroupAddUpdateConfigView,
    GroupConfigDeleteView,
    GroupConfigModalView,
    GroupCreateView,
    GroupDeleteView,
    GroupDetailView,
    GroupUpdateView,
    RuleFormModalView,
)
from .host import (
    ConfigDiffView,
    HostConfigView,
    HostCreateView,
    HostDeleteView,
    HostDetailView,
    HostRefreshConfigView,
    HostUpdateView,
    HostUpgradeView,
)
from .network import (
    NetworkCreateView,
    NetworkDeleteView,
    NetworkDetailView,
    NetworkListView,
    NetworkMemberAddView,
    NetworkMemberDeleteView,
    NetworkMemberEditView,
    NetworkUpdateView,
)
from .rollout import (
    RolloutCreateView,
    RolloutDeleteView,
    RolloutDetailView,
    RolloutUpdateView,
    UnfreezeHostConfigView,
)
from .rule import RuleCreateView, RuleDeleteView, RuleDetailView, RuleUpdateView
from .template import (
    TemplateCreateView,
    TemplateDeleteView,
    TemplateDetailView,
    TemplateUpdateView,
)
