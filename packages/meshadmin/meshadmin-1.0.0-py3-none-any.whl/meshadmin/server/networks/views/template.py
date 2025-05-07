from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from meshadmin.server.networks.forms import TemplateForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import Network, Template
from meshadmin.server.networks.services import generate_enrollment_token


class TemplateDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = Template
    template_name = "networks/template/detail.html"

    def get_network(self):
        return self.get_object().network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fields"] = [
            {
                "name": field.name,
                "verbose_name": field.verbose_name,
                "value": getattr(self.object, field.name),
            }
            for field in self.model._meta.fields
        ]
        context.update(
            {
                "network": self.object.network,
                "groups": self.object.groups.all(),
                "server_url": settings.MESH_SERVER_URL,
                "enrollment_token": generate_enrollment_token(self.object),
            }
        )
        return context


class TemplateCreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = Template
    form_class = TemplateForm
    template_name = "networks/template/form.html"

    def get_network(self):
        return get_object_or_404(Network, id=self.kwargs.get("network_id"))

    def get_success_url(self):
        return reverse_lazy("networks:template-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        network_id = self.kwargs.get("network_id")
        if network_id:
            network = get_object_or_404(Network, id=network_id)
            kwargs["initial"] = {"network_id": network_id}
            kwargs["network"] = network
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        context["model_name"] = self.model._meta.verbose_name
        network_id = self.kwargs.get("network_id")
        context["network_id"] = network_id
        if network_id:
            context["network"] = get_object_or_404(Network, id=network_id)
        return context

    def form_valid(self, form):
        network_id = self.kwargs.get("network_id")
        if network_id:
            form.instance.network_id = network_id
        return super().form_valid(form)


class TemplateUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = "networks/template/form.html"

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return reverse_lazy("networks:template-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"network_id": self.object.network_id}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["model_name"] = self.model._meta.verbose_name
        return context


class TemplateDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = Template
    template_name = "networks/shared/delete.html"
    success_url = reverse_lazy("networks:template-list")

    def get_network(self):
        return self.get_object().network

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.object.network.pk}
            )
            + "#templates-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context
