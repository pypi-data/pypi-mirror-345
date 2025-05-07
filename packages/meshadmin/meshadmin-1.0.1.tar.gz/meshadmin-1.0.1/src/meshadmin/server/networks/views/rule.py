from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from meshadmin.server.networks.forms import RuleForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import Group, Rule


class RuleDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = Rule
    template_name = "networks/rule/detail.html"

    def get_network(self):
        return self.get_object().security_group.network

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
        return context


class RuleCreateView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = "networks/rule/form.html"

    def get_network(self):
        security_group_id = self.kwargs.get("security_group_id")
        if security_group_id:
            security_group = get_object_or_404(Group, id=security_group_id)
            return security_group.network
        return None

    def get_success_url(self):
        return reverse_lazy("networks:rule-detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        security_group_id = self.kwargs.get("security_group_id")
        if security_group_id:
            kwargs["initial"] = {"security_group_id": security_group_id}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        context["model_name"] = self.model._meta.verbose_name
        security_group_id = self.kwargs.get("security_group_id")
        if security_group_id:
            context["security_group"] = get_object_or_404(Group, id=security_group_id)
        return context

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        security_group_id = self.kwargs.get("security_group_id")
        if security_group_id:
            form.instance.security_group_id = security_group_id
        return super().form_valid(form)


class RuleUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = Rule
    form_class = RuleForm
    template_name = "networks/rule/form.html"

    def get_network(self):
        return self.get_object().security_group.network

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["security_group"] = self.object.security_group
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"security_group_id": self.object.security_group_id}
        return kwargs

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("networks:rule-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            context = {
                "rules": self.object.security_group.rules.all(),
            }
            return render(self.request, "networks/group/_rules_list.html", context)
        return response


class RuleDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = Rule
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().security_group.network

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.htmx:
            return HttpResponse("")

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail",
                kwargs={"pk": self.object.security_group.network.pk},
            )
            + "#groups-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context
