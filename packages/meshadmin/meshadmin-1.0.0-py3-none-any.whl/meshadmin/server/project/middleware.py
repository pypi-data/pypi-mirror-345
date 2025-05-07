from django.urls import resolve, reverse

from meshadmin.server.networks.models import (
    CA,
    ConfigRollout,
    Group,
    Host,
    Network,
    Rule,
    Template,
)


class BreadcrumbMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if request.htmx:
            return response

        if not hasattr(response, "context_data"):
            return response

        # Start with the base networks link
        breadcrumbs = [{"label": "Networks", "url": reverse("networks:network-list")}]

        # Get resolved URL info
        resolved = resolve(request.path_info)
        url_name = resolved.url_name
        kwargs = resolved.kwargs
        context = response.context_data

        # Handle network-specific paths
        if "pk" in kwargs and url_name in [
            "network-detail",
            "network-edit",
            "network-delete",
        ]:
            network_id = kwargs["pk"]
            network = self._get_network_by_id(network_id, context)
            if network:
                breadcrumbs.append(
                    {
                        "label": network.name,
                        "url": reverse(
                            "networks:network-detail", kwargs={"pk": network.pk}
                        ),
                    }
                )
                if url_name == "network-edit":
                    breadcrumbs.append({"label": "Edit", "url": "#"})
                elif url_name == "network-delete":
                    breadcrumbs.append({"label": "Delete", "url": "#"})

        # Handle network creation
        elif url_name == "network-create":
            breadcrumbs.append({"label": "Create Network", "url": "#"})

        # Handle network-related entities (host, template, group, ca, rollout, membership)
        elif "network_id" in kwargs:
            network_id = kwargs["network_id"]
            network = self._get_network_by_id(network_id, context)

            if network:
                # Add network link with appropriate section anchor
                section_anchor = ""
                if "host" in url_name:
                    section_anchor = "#hosts-section"
                elif "template" in url_name:
                    section_anchor = "#templates-section"
                elif "group" in url_name or "security-group" in url_name:
                    section_anchor = "#groups-section"
                elif "ca" in url_name:
                    section_anchor = "#cas-section"
                elif "rollout" in url_name:
                    section_anchor = "#rollouts-section"
                elif "member" in url_name or "member" in url_name:
                    section_anchor = "#members-section"

                breadcrumbs.append(
                    {
                        "label": network.name,
                        "url": reverse(
                            "networks:network-detail", kwargs={"pk": network.pk}
                        )
                        + section_anchor,
                    }
                )

                # Add entity-specific breadcrumbs based on URL pattern
                if "host" in url_name:
                    breadcrumbs.append({"label": "Create Host", "url": "#"})
                elif "template" in url_name:
                    breadcrumbs.append({"label": "Create Template", "url": "#"})
                elif "group" in url_name:
                    breadcrumbs.append({"label": "Create Group", "url": "#"})
                elif "ca" in url_name:
                    breadcrumbs.append({"label": "Create CA", "url": "#"})
                elif "rollout" in url_name:
                    breadcrumbs.append({"label": "Create Rollout", "url": "#"})
                elif "add" in url_name:
                    breadcrumbs.append({"label": "Add Member", "url": "#"})

        # Handle entity-specific paths (without network_id in URL)
        elif "pk" in kwargs:
            entity_id = kwargs["pk"]

            # Handle Host
            if url_name in [
                "host-detail",
                "host-edit",
                "host-delete",
            ]:
                host = self._get_object_by_id(Host, entity_id, context)
                if host:
                    network = host.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#hosts-section",
                        }
                    )
                    breadcrumbs.append(
                        {
                            "label": host.name,
                            "url": reverse(
                                "networks:host-detail", kwargs={"pk": host.pk}
                            ),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

            # Handle Template
            elif url_name in ["template-detail", "template-edit", "template-delete"]:
                template = self._get_object_by_id(Template, entity_id, context)
                if template:
                    network = template.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#templates-section",
                        }
                    )
                    breadcrumbs.append(
                        {
                            "label": template.name,
                            "url": reverse(
                                "networks:template-detail", kwargs={"pk": template.pk}
                            ),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

            # Handle Group
            elif url_name in ["group-detail", "group-edit", "group-delete"]:
                group = self._get_object_by_id(Group, entity_id, context)
                if group:
                    network = group.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#groups-section",
                        }
                    )
                    breadcrumbs.append(
                        {
                            "label": group.name,
                            "url": reverse(
                                "networks:group-detail", kwargs={"pk": group.pk}
                            ),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

            # Handle CA
            elif url_name in ["ca-detail", "ca-edit", "ca-delete"]:
                ca = self._get_object_by_id(CA, entity_id, context)
                if ca:
                    network = ca.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#cas-section",
                        }
                    )
                    breadcrumbs.append(
                        {
                            "label": ca.name,
                            "url": reverse("networks:ca-detail", kwargs={"pk": ca.pk}),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

            # Handle Rule
            elif url_name in ["rule-detail", "rule-edit", "rule-delete"]:
                rule = self._get_object_by_id(Rule, entity_id, context)
                if rule:
                    security_group = rule.security_group
                    network = security_group.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#groups-section",
                        }
                    )
                    if security_group:
                        breadcrumbs.append(
                            {
                                "label": security_group.name,
                                "url": reverse(
                                    "networks:group-detail",
                                    kwargs={"pk": security_group.pk},
                                ),
                            }
                        )
                    breadcrumbs.append(
                        {
                            "label": f"Rule {rule.pk}",
                            "url": reverse(
                                "networks:rule-detail", kwargs={"pk": rule.pk}
                            ),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

            # Handle Rollout
            elif url_name in [
                "rollout-detail",
                "rollout-edit",
                "rollout-delete",
            ]:
                rollout = self._get_object_by_id(ConfigRollout, entity_id, context)
                if rollout:
                    network = rollout.network
                    breadcrumbs.append(
                        {
                            "label": network.name,
                            "url": reverse(
                                "networks:network-detail", kwargs={"pk": network.pk}
                            )
                            + "#rollouts-section",
                        }
                    )
                    breadcrumbs.append(
                        {
                            "label": f"Rollout {rollout.pk}",
                            "url": reverse(
                                "networks:rollout-detail", kwargs={"pk": rollout.pk}
                            ),
                        }
                    )

                    # Add action breadcrumb
                    if "edit" in url_name:
                        breadcrumbs.append({"label": "Edit", "url": "#"})
                    elif "delete" in url_name:
                        breadcrumbs.append({"label": "Delete", "url": "#"})

        # Add breadcrumbs to context
        response.context_data["breadcrumbs"] = breadcrumbs
        return response

    def _get_network_by_id(self, network_id, context):
        """
        Helper to get a network by ID from context or database
        """
        if (
            "network" in context
            and hasattr(context["network"], "pk")
            and context["network"].pk == network_id
        ):
            return context["network"]

        if (
            "object" in context
            and isinstance(context["object"], Network)
            and context["object"].pk == network_id
        ):
            return context["object"]

        try:
            return Network.objects.get(id=network_id)
        except Network.DoesNotExist:
            return None

    def _get_object_by_id(self, model_class, object_id, context):
        """
        Helper to get an object by ID from context or database
        """
        if (
            "object" in context
            and isinstance(context["object"], model_class)
            and context["object"].pk == object_id
        ):
            return context["object"]

        try:
            return model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            return None
