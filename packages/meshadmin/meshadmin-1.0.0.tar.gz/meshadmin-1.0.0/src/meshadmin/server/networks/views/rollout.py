from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import ConfigRollout, Host, Network


class RolloutCreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = ConfigRollout
    template_name = "networks/rollout/create.html"
    fields = ["name", "notes"]

    def get_network(self):
        network_id = self.kwargs.get("network_id")
        if network_id:
            return get_object_or_404(Network, id=network_id)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        network = self.get_network()
        context["network"] = network

        host_ids = self.request.GET.get("hosts", "").split(",")
        if host_ids and host_ids[0]:
            context["preselected_hosts"] = Host.objects.filter(
                id__in=host_ids, network=network
            )

        context["hosts"] = Host.objects.filter(network=network)
        return context

    def form_valid(self, form):
        form.instance.network_id = self.kwargs["network_id"]
        response = super().form_valid(form)

        selected_hosts = self.request.POST.getlist("hosts")
        if selected_hosts:
            self.object.target_hosts.set(selected_hosts)
            Host.objects.filter(id__in=selected_hosts).update(config_freeze=True)

        return response

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.kwargs["network_id"]}
            )
            + "#rollouts-section"
        )


class RolloutDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = ConfigRollout
    template_name = "networks/rollout/detail.html"

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_hosts"] = self.object.target_hosts.exclude(
            id__in=self.object.completed_hosts.values_list("id", flat=True)
        )
        return context


class UnfreezeHostConfigView(LoginRequiredMixin, NetworkPermissionMixin, View):
    def get_network(self):
        rollout = get_object_or_404(ConfigRollout, id=self.kwargs.get("pk"))
        return rollout.network

    def post(self, request, pk):
        rollout = get_object_or_404(ConfigRollout, id=pk)
        host_id = request.POST.get("host_id")
        if host_id:
            host = get_object_or_404(Host, id=host_id)
            if host not in rollout.completed_hosts.all():
                try:
                    host.config_freeze = False
                    host.save()
                    rollout.completed_hosts.add(host)
                except Exception:
                    rollout.status = "FAILED"
                    rollout.save()
        else:
            pending_hosts = rollout.target_hosts.exclude(
                id__in=rollout.completed_hosts.values_list("id", flat=True)
            )
            for host in pending_hosts:
                try:
                    host.config_freeze = False
                    host.save()
                    rollout.completed_hosts.add(host)
                except Exception:
                    rollout.status = "FAILED"
                    rollout.save()
                    return redirect("networks:rollout-detail", pk=pk)

        if not rollout.target_hosts.exclude(
            id__in=rollout.completed_hosts.values_list("id", flat=True)
        ).exists():
            rollout.status = "COMPLETED"
            rollout.save()

        return redirect("networks:rollout-detail", pk=pk)


class RolloutUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = ConfigRollout
    template_name = "networks/rollout/edit.html"
    fields = ["name", "notes"]

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hosts"] = Host.objects.filter(network=self.get_network())
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        selected_hosts = self.request.POST.getlist("hosts")
        if selected_hosts:
            removed_hosts = self.object.target_hosts.exclude(id__in=selected_hosts)
            removed_hosts.update(config_freeze=False)
            self.object.target_hosts.set(selected_hosts)
            Host.objects.filter(id__in=selected_hosts).update(config_freeze=True)

        return response

    def get_success_url(self):
        return reverse_lazy("networks:rollout-detail", kwargs={"pk": self.object.pk})


class RolloutDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = ConfigRollout
    template_name = "networks/rollout/delete.html"

    def get_network(self):
        return self.get_object().network

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.target_hosts.all().update(config_freeze=False)
        network_id = self.object.network_id
        self.object.delete()
        return HttpResponseRedirect(
            reverse_lazy("networks:network-detail", kwargs={"pk": network_id})
            + "#rollouts-section"
        )
