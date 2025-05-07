import difflib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from meshadmin.server.networks.forms import HostForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import Host, HostConfig, Network
from meshadmin.server.networks.services import generate_config_yaml


class HostDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = Host
    template_name = "networks/host/detail.html"

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            {
                "name": field.name,
                "verbose_name": field.verbose_name,
                "value": getattr(self.object, field.name),
            }
            for field in self.model._meta.fields
        ]
        config_history = self.object.hostconfig_set.order_by("-created_at")
        context.update(
            {
                "fields": fields,
                "network": self.object.network,
                "groups": self.object.groups.all(),
                "config": config_history.first(),
                "config_history": config_history,
            }
        )
        return context


class HostCreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = Host
    form_class = HostForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return get_object_or_404(Network, id=self.kwargs.get("network_id"))

    def get_success_url(self):
        return reverse_lazy("networks:host-detail", kwargs={"pk": self.object.pk})

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


class HostUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = Host
    form_class = HostForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return reverse_lazy("networks:host-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        return context


class HostDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = Host
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.object.network.pk}
            )
            + "#hosts-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context


class HostConfigView(LoginRequiredMixin, View):
    def get(self, request, pk):
        get_object_or_404(Host, id=pk)
        config = generate_config_yaml(pk)
        return HttpResponse(config, content_type="text/yaml")


class ConfigDiffView(LoginRequiredMixin, View):
    def get(self, request, base_id, compare_id):
        try:
            base_config = get_object_or_404(HostConfig, id=base_id)
            compare_config = get_object_or_404(HostConfig, id=compare_id)
            diff = list(
                difflib.unified_diff(
                    base_config.config.splitlines(),
                    compare_config.config.splitlines(),
                    fromfile=f"Version {base_config.created_at:%Y-%m-%d %H:%M}",
                    tofile=f"Version {compare_config.created_at:%Y-%m-%d %H:%M}",
                    lineterm="",
                )
            )
            context = {
                "diff": diff,
                "has_changes": bool(diff),
                "base_time": base_config.created_at.strftime("%Y-%m-%d %H:%M"),
                "compare_time": compare_config.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            return render(request, "networks/host/diff.html", context)
        except Exception:
            context = {"error": "Error generating diff"}
            return render(request, "networks/host/diff.html", context)


class HostRefreshConfigView(LoginRequiredMixin, View):
    def post(self, request, pk, rollout_id):
        host = get_object_or_404(Host, id=pk)
        generate_config_yaml(host.id, ignore_freeze=True)
        return redirect("networks:rollout-detail", pk=rollout_id)


class HostUpgradeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        host = get_object_or_404(Host, id=pk)
        host.upgrade_requested = True
        host.save()
        return render(request, "networks/host/upgrade_button.html", {"object": host})
