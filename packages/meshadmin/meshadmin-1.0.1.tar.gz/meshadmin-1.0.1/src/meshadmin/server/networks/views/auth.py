from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views import View


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            SocialAccount.objects.get(user=request.user)
            logout(request)
            return HttpResponseRedirect(
                f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout?post_logout_redirect_uri={settings.MESH_SERVER_URL}&client_id={settings.KEYCLOAK_REALM}"
            )
        except SocialAccount.DoesNotExist:
            logout(request)
            return HttpResponseRedirect(reverse("networks:network-list"))
