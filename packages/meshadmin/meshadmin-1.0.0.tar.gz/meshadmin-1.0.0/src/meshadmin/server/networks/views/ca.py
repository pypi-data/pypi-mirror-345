from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from meshadmin.server.networks.forms import CAForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import CA, Host, Network, SigningCA


class CADetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = CA
    template_name = "networks/ca/detail.html"

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
        context.update(
            {
                "fields": fields,
                "network": self.object.network,
                "hosts": Host.objects.filter(
                    id__in=self.object.hostcert_set.values_list("host_id", flat=True)
                ).select_related("network"),
            }
        )
        return context


class CACreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = CA
    form_class = CAForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return get_object_or_404(Network, id=self.kwargs.get("network_id"))

    def get_success_url(self) -> str:
        return reverse_lazy("networks:ca-detail", kwargs={"pk": self.object.pk})

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


class CAUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = CA
    form_class = CAForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return reverse_lazy("networks:ca-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["model_name"] = self.model._meta.verbose_name
        return context


class CADeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = CA
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.object.network.pk}
            )
            + "#cas-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context


class CAMakeSigningView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ca = get_object_or_404(CA, pk=pk)
        network = ca.network
        SigningCA.objects.filter(network=network).delete()
        SigningCA.objects.create(network=network, ca=ca)
        context = {"cas": CA.objects.filter(network=network)}
        return HttpResponse(
            render_to_string(
                "networks/network/_cas_table.html", context, request=request
            )
        )
