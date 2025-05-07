from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from meshadmin.server.networks.forms import GroupConfigForm, GroupForm, RuleForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import Group, GroupConfig, Network, Rule


class GroupDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = Group
    template_name = "networks/group/detail.html"

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hosts = self.object.host_set.all()
        search = self.request.GET.get("search", "")
        if search:
            hosts = hosts.filter(name__icontains=search)

        if self.request.GET.get("stale_config"):
            from datetime import timedelta

            from django.utils import timezone

            stale_threshold = timezone.now() - timedelta(hours=24)
            hosts = hosts.filter(
                models.Q(last_config_refresh__lt=stale_threshold)
                | models.Q(last_config_refresh__isnull=True)
            )

        per_page = int(self.request.GET.get("per_page", settings.PAGINATION_PER_PAGE))
        paginator = Paginator(hosts, per_page)
        page = self.request.GET.get("hosts_page", 1)

        try:
            hosts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            hosts = paginator.page(1)

        context.update(
            {
                "hosts": hosts,
                "paginator": paginator,
                "page_obj": hosts,
                "per_page": per_page,
                "per_page_options": [25, 50, 100],
                "network": self.object.network,
                "fields": [
                    {
                        "name": field.name,
                        "verbose_name": field.verbose_name,
                        "value": getattr(self.object, field.name),
                    }
                    for field in self.model._meta.fields
                ],
                "rules": self.object.rules.all(),
                "configs": self.object.config_overrides.all(),
            }
        )
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["networks/network/_hosts_table.html"]
        return [self.template_name]


class GroupCreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "networks/group/form.html"

    def get_network(self):
        return get_object_or_404(Network, id=self.kwargs.get("network_id"))

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            context = self.get_context_data()
            context["object"] = self.object
            context["action"] = "Update"
            return render(self.request, "networks/group/_form_content.html", context)
        return response

    def get_success_url(self):
        return reverse_lazy("networks:group-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        network_id = self.kwargs.get("network_id")
        if network_id:
            network = get_object_or_404(Network, id=network_id)
            kwargs["network"] = network
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "action": "Create",
                "model_name": self.model._meta.verbose_name,
                "network_id": self.kwargs.get("network_id"),
            }
        )
        return context


class GroupUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "networks/group/form.html"

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "action": "Update",
                "network_id": self.get_object().network.id,
                "rules": self.get_object().rules.all(),
            }
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            context = self.get_context_data()
            context["object"] = self.object
            context["action"] = "Update"
            return render(self.request, "networks/group/_form_content.html", context)
        return response

    def get_success_url(self):
        return reverse_lazy("networks:group-detail", kwargs={"pk": self.object.pk})


class GroupDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = Group
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.object.network.pk}
            )
            + "#groups-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context


class RuleFormModalView(LoginRequiredMixin, NetworkPermissionMixin, View):
    def get_network(self):
        group = get_object_or_404(Group, id=self.request.GET.get("group"))
        return group.network

    def get(self, request):
        group_id = request.GET.get("group")
        rule_id = request.GET.get("rule")
        security_group = get_object_or_404(Group, id=group_id)

        if rule_id:
            rule = get_object_or_404(Rule, id=rule_id)
            form = RuleForm(instance=rule)
        else:
            form = RuleForm(
                initial={"security_group": security_group},
                instance=Rule(security_group=security_group),
            )

        return render(
            request,
            "networks/rule/_form_modal.html",
            {
                "form": form,
                "security_group": security_group,
                "rule": rule if rule_id else None,
            },
        )


class GroupAddRuleView(LoginRequiredMixin, NetworkPermissionMixin, View):
    def get_network(self):
        group_id = self.request.POST.get("security_group")
        group = get_object_or_404(Group, id=group_id)
        return group.network

    def post(self, request):
        group_id = request.POST.get("security_group")
        security_group = get_object_or_404(Group, id=group_id)

        form = RuleForm(request.POST, initial={"security_group_id": group_id})
        if form.is_valid():
            rule = form.save(commit=False)
            rule.security_group = security_group
            rule.save()

            if request.POST.getlist("groups"):
                rule.groups.set(
                    Group.objects.filter(id__in=request.POST.getlist("groups"))
                )

            context = {"rules": Rule.objects.filter(security_group=security_group)}
            return render(
                request,
                "networks/group/_rules_list.html",
                context,
            )
        else:
            response = render(
                request,
                "networks/rule/_form_modal.html",
                {
                    "form": form,
                    "security_group": security_group,
                },
            )
            response["HX-Retarget"] = "#modal-content"
            return response


class GroupConfigModalView(LoginRequiredMixin, NetworkPermissionMixin, View):
    def get_network(self):
        group = get_object_or_404(Group, id=self.request.GET.get("group"))
        return group.network

    def get(self, request):
        group_id = request.GET.get("group")
        config_id = request.GET.get("config")
        group = get_object_or_404(Group, id=group_id)

        if config_id:
            config = get_object_or_404(GroupConfig, id=config_id)
            form = GroupConfigForm(instance=config)
        else:
            form = GroupConfigForm(
                instance=GroupConfig(group=group),
            )

        return render(
            request,
            "networks/group/_config_modal.html",
            {
                "form": form,
                "group": group,
                "config": config if config_id else None,
            },
        )


class GroupAddUpdateConfigView(LoginRequiredMixin, NetworkPermissionMixin, View):
    def get_network(self):
        group = get_object_or_404(Group, id=self.request.POST.get("group"))
        return group.network

    def post(self, request):
        group_id = request.POST.get("group")
        config_id = request.POST.get("config")
        group = get_object_or_404(Group, id=group_id)

        if config_id:
            config = get_object_or_404(GroupConfig, id=config_id)
            form = GroupConfigForm(request.POST, instance=config)
        else:
            form = GroupConfigForm(request.POST)

        if form.is_valid():
            config = form.save(commit=False)
            config.group = group
            config.save()
            return render(
                request,
                "networks/group/_configs_list.html",
                {
                    "configs": group.config_overrides.all(),
                },
            )
        else:
            response = render(
                request,
                "networks/group/_config_modal.html",
                {
                    "form": form,
                    "group": group,
                    "config": config if config_id else None,
                },
            )
            response["HX-Retarget"] = "#config-modal-content"
            return response


class GroupConfigDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = GroupConfig
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().group.network

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse("")

    def get_success_url(self):
        return (
            reverse_lazy("networks:group-detail", kwargs={"pk": self.object.group.pk})
            + "#groups-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context
