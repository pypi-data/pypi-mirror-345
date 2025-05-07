from django.contrib import admin
from django.urls import include, path

from meshadmin.server.networks.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("meshadmin.server.networks.urls", namespace="networks")),
]
