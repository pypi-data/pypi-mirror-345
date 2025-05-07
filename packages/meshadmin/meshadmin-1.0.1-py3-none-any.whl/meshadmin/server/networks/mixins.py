from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from meshadmin.server.networks.models import Network, NetworkMembership


class NetworkPermissionMixin(UserPassesTestMixin):
    def get_network(self):
        if hasattr(self, "object") and isinstance(self.object, Network):
            return self.object

        network_id = self.kwargs.get("network_id") or self.kwargs.get("pk")
        if network_id:
            return get_object_or_404(Network, id=network_id)

        if hasattr(self, "object"):
            return self.object.network

        return None

    def test_func(self):
        network = self.get_network()
        if not network:
            return False

        if self.request.user.is_superuser:
            return True

        return NetworkMembership.objects.filter(
            network=network,
            user=self.request.user,
            role__in=[NetworkMembership.Role.ADMIN, NetworkMembership.Role.MEMBER],
        ).exists()
