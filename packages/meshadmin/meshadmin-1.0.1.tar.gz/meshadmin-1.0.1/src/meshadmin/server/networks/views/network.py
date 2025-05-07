from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    QueryDict,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from meshadmin.server.networks.forms import NetworkForm, NetworkMembershipForm
from meshadmin.server.networks.mixins import NetworkPermissionMixin
from meshadmin.server.networks.models import Network, NetworkMembership


class NetworkListView(LoginRequiredMixin, ListView):
    model = Network
    template_name = "networks/network/list.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Network.objects.all()
        return Network.objects.filter(
            memberships__user=self.request.user,
            memberships__role__in=[
                NetworkMembership.Role.ADMIN,
                NetworkMembership.Role.MEMBER,
            ],
        )


class NetworkDetailView(LoginRequiredMixin, NetworkPermissionMixin, DetailView):
    model = Network
    template_name = "networks/network/detail.html"
    context_object_name = "network"

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
                "templates": self.object.template_set.all(),
                "groups": self.object.group_set.all(),
                "cas": self.object.ca_set.all(),
                "rollouts": self.object.configrollout_set.all(),
                "now": now(),
                "memberships": self.object.memberships.select_related("user").all(),
            }
        )
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["networks/network/_hosts_table.html"]
        return [self.template_name]


class NetworkCreateView(LoginRequiredMixin, CreateView):
    model = Network
    form_class = NetworkForm
    template_name = "networks/shared/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return (
            reverse_lazy("networks:network-detail", kwargs={"pk": self.object.pk})
            + "#templates-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        context["model_name"] = self.model._meta.verbose_name
        return context


class NetworkUpdateView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = Network
    form_class = NetworkForm
    template_name = "networks/shared/form.html"

    def get_success_url(self):
        return reverse_lazy("networks:network-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["model_name"] = self.model._meta.verbose_name
        return context


class NetworkDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = Network
    template_name = "networks/shared/delete.html"
    success_url = reverse_lazy("networks:network-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.verbose_name
        return context


class NetworkMemberAddView(LoginRequiredMixin, NetworkPermissionMixin, CreateView):
    model = NetworkMembership
    form_class = NetworkMembershipForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return get_object_or_404(Network, id=self.kwargs.get("network_id"))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["network"] = self.get_network()
        return kwargs

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.kwargs["network_id"]}
            )
            + "#members-section"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add Member"
        context["model_name"] = self.model._meta.verbose_name
        context["network_id"] = self.kwargs["network_id"]
        return context


class NetworkMemberEditView(LoginRequiredMixin, NetworkPermissionMixin, UpdateView):
    model = NetworkMembership
    form_class = NetworkMembershipForm
    template_name = "networks/shared/form.html"

    def get_network(self):
        return self.get_object().network

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            context = self.get_context_data()
            return render(self.request, "networks/network/_member_row.html", context)
        return super().form_valid(form)

    def put(self, request, *args, **kwargs):
        membership = self.get_object()
        data = QueryDict(request.body)
        role = data.get("role")
        if role in [NetworkMembership.Role.ADMIN, NetworkMembership.Role.MEMBER]:
            membership.role = role
            membership.save()
            context = {"membership": membership, "network": membership.network}
            return render(request, "networks/network/_member_row.html", context)
        return HttpResponseBadRequest()


class NetworkMemberDeleteView(LoginRequiredMixin, NetworkPermissionMixin, DeleteView):
    model = NetworkMembership
    template_name = "networks/shared/delete.html"

    def get_network(self):
        return self.get_object().network

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse("")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return (
            reverse_lazy(
                "networks:network-detail", kwargs={"pk": self.get_object().network.id}
            )
            + "#members-section"
        )
