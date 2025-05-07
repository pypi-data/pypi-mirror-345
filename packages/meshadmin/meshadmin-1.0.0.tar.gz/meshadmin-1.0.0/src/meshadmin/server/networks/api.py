import json
import os
import time
from datetime import timedelta
from typing import Optional

import jwt
import requests
import structlog
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from jwcrypto.jwk import JWK
from ninja import NinjaAPI
from ninja.security import HttpBearer

from meshadmin.common import schemas
from meshadmin.server.assets import asset_path
from meshadmin.server.networks.models import Host, Network, NetworkMembership, Template
from meshadmin.server.networks.services import (
    create_network,
    create_template,
    enrollment,
    generate_config_yaml,
    generate_enrollment_token,
)

logger = structlog.get_logger(__name__)

User = get_user_model()


class KeycloakAuthBearer(HttpBearer):
    def __init__(self):
        super().__init__()
        self.jwks = None

    def get_keycloak_public_key(self):
        if not self.jwks:
            response = requests.get(settings.KEYCLOAK_CERTS_URL)
            response.raise_for_status()
            self.jwks = response.json()
        return self.jwks

    def authenticate(self, request: HttpRequest, token: str) -> Optional[str]:
        try:
            if os.getenv("MESHADMIN_TEST_MODE") == "true":
                logger.info("test mode enabled, setting user to admin")
                request.user = User.objects.get(username="admin")
                return token

            unverified_headers = jwt.get_unverified_header(token)
            kid = unverified_headers["kid"]
            jwks = self.get_keycloak_public_key()
            public_key = None
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break

            if not public_key:
                logger.error("No matching public key found")
                return None

            data = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_signature": True},
                issuer=settings.KEYCLOAK_ISSUER,
            )
            if data.get("azp") != settings.KEYCLOAK_ADMIN_CLIENT:
                return None

            email = data.get("email")
            if not email:
                logger.error("No email found in token")
                return None

            user = User.objects.filter(email=email).first()
            if not user:
                logger.error("User not found", email=email)
                return None

            request.user = user
            return token
        except (
            jwt.InvalidTokenError,
            jwt.ExpiredSignatureError,
            requests.RequestException,
        ) as e:
            logger.error("Token validation failed", error=str(e))
            return None


keycloak_auth = KeycloakAuthBearer()

api = NinjaAPI(title="MeshAdmin API")


@api.get("/nebula/download/{os_name}/{architecture}/{binary_name}")
def download_nebula_binary(request, os_name: str, architecture: str, binary_name: str):
    valid_os = ["Linux", "Darwin"]
    valid_binaries = ["nebula", "nebula-cert"]
    valid_architectures = {"Darwin": ["arm64"], "Linux": ["aarch64", "x86_64"]}

    if os_name not in valid_os:
        return HttpResponse(
            f"Invalid OS: {os_name}. Only Linux and Darwin are supported.", status=400
        )

    if (
        os_name not in valid_architectures
        or architecture not in valid_architectures[os_name]
    ):
        return HttpResponse(
            f"Invalid architecture: {architecture} for {os_name}. "
            f"Supported architectures for {os_name}: {valid_architectures.get(os_name, [])}",
            status=400,
        )

    if binary_name not in valid_binaries:
        return HttpResponse(f"Invalid binary name: {binary_name}", status=400)

    binary_path = asset_path / os_name / architecture / binary_name
    if not binary_path.exists():
        return HttpResponse(
            f"Binary not found: {binary_name} for {os_name}/{architecture}", status=404
        )

    return FileResponse(
        open(binary_path, "rb"),
        as_attachment=True,
        filename=binary_name,
        content_type="application/octet-stream",
    )


@api.post("/enroll", url_name="enroll", auth=None)
@transaction.atomic
def enroll(request: HttpRequest, client_enrollment: schemas.ClientEnrollment):
    logger.info(
        "enrollment request received",
        enrollment_key=client_enrollment.enrollment_key,
        preferred_hostname=client_enrollment.preferred_hostname,
        public_ip=client_enrollment.public_ip,
    )

    try:
        host = enrollment(
            client_enrollment.enrollment_key,
            client_enrollment.public_auth_key,
            client_enrollment.enroll_on_existence,
            client_enrollment.public_ip,
            client_enrollment.preferred_hostname,
            client_enrollment.public_net_key,
            client_enrollment.interface,
        )
        logger.info(
            "host enrolled successfully",
            host_id=host.id,
            network_name=host.network.name,
            hostname=host.name,
            interface=host.interface,
        )
        return HttpResponse(f"Enrolled host {host.id} in network {host.network.name}")
    except Exception as e:
        logger.error("enrollment failed", error=str(e))
        raise


@api.get("/config")
def get_config(request: HttpRequest):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        logger.warning("config request missing authorization")
        return HttpResponse(status=403, content="Authorization bearer token missing")

    token = bearer_token.split("Bearer ")[1]
    try:
        data = jwt.decode(
            token, algorithms=["RS256"], options={"verify_signature": False}
        )
        try:
            host = get_object_or_404(Host, public_auth_kid=data["kid"])
        except Http404:
            logger.warning("host not found for token kid", kid=data.get("kid"))
            return HttpResponse(
                "Host not found for authentication token",
                status=401,
                content_type="text/plain",
            )

        try:
            pem_public_key = JWK.from_json(host.public_auth_key).export_to_pem()
            jwt.decode(token, key=pem_public_key, algorithms=["RS256"])
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as e:
            logger.warning("invalid authentication token", error=str(e))
            return HttpResponse(
                "Invalid authentication token", status=401, content_type="text/plain"
            )

        start = time.time()
        config = generate_config_yaml(host.pk)
        duration = time.time() - start

        if host.last_config_refresh != config:
            logger.info(
                "config changed",
                host_id=host.id,
                host_name=host.name,
                duration=duration,
            )
            host.last_config_refresh = now()
            host.save()
        else:
            logger.debug(
                "config unchanged",
                host_id=host.id,
                host_name=host.name,
                duration=duration,
            )

        cli_version = request.headers.get("X-Meshadmin-Version")
        if cli_version and host.cli_version != cli_version:
            logger.info(
                "Mismatch detected. Updating the version in the database",
                host_id=host.id,
                host_name=host.name,
                cli_version=cli_version,
            )
            host.cli_version = cli_version
            host.save()

        response = HttpResponse(config, content_type="text/yaml")
        response["X-Update-Interval"] = str(host.network.update_interval)
        if host.upgrade_requested:
            logger.info(
                "upgrade requested",
                host_id=host.id,
                host_name=host.name,
                cli_version=cli_version,
            )
            response["X-Upgrade-Requested"] = "true"
            host.upgrade_requested = False
            host.save()
        return response
    except Exception as e:
        logger.error("config generation failed", error=str(e))
        return HttpResponse(
            f"Failed to generate config: {str(e)}",
            status=500,
            content_type="text/plain",
        )


@api.post("/cleanup-ephemeral")
def cleanup_ephemeral_hosts(request: HttpRequest):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        logger.warning("cleanup request missing authorization")
        return HttpResponse(status=403, content="Authorization bearer token missing")

    token = bearer_token.split("Bearer ")[1]
    try:
        data = jwt.decode(
            token, algorithms=["RS256"], options={"verify_signature": False}
        )
        try:
            host = get_object_or_404(Host, public_auth_kid=data["kid"])
        except Http404:
            logger.warning("host not found for token kid", kid=data.get("kid"))
            return HttpResponse(
                "Host not found for authentication token",
                status=401,
                content_type="text/plain",
            )

        try:
            pem_public_key = JWK.from_json(host.public_auth_key).export_to_pem()
            jwt.decode(token, key=pem_public_key, algorithms=["RS256"])
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as e:
            logger.warning("invalid authentication token", error=str(e))
            return HttpResponse(
                "Invalid authentication token", status=401, content_type="text/plain"
            )

        cutoff = timezone.now() - timedelta(minutes=10)
        stale_hosts = Host.objects.filter(
            network=host.network, is_ephemeral=True, last_config_refresh__lt=cutoff
        )
        count = 0
        for stale_host in stale_hosts:
            logger.info(
                "removing stale ephemeral host",
                host_id=stale_host.id,
                host_name=stale_host.name,
                network=stale_host.network.name,
                last_refresh=stale_host.last_config_refresh,
            )
            stale_host.delete()
            count += 1

        return {"removed_count": count}

    except Exception as e:
        logger.error("cleanup failed", error=str(e))
        return HttpResponse(
            f"Failed to clean up ephemeral hosts: {str(e)}",
            status=500,
            content_type="text/plain",
        )


@api.post("/networks", response=schemas.NetworkResponse, auth=keycloak_auth)
def create_network_endpoint(request: HttpRequest, data: schemas.NetworkCreate):
    network = create_network(
        network_name=data.name, network_cidr=data.cidr, user=request.user
    )
    return {"id": network.id, "name": network.name, "cidr": network.cidr}


@api.get("/networks", auth=keycloak_auth)
def list_networks(request: HttpRequest):
    if request.user.is_superuser:
        networks = Network.objects.all()
    else:
        networks = Network.objects.filter(
            memberships__user=request.user,
            memberships__role=NetworkMembership.Role.ADMIN,
        )
    return [
        {"id": network.id, "name": network.name, "cidr": network.cidr}
        for network in networks
    ]


@api.delete("/networks/{name}", auth=keycloak_auth)
def delete_network(request: HttpRequest, name: str):
    try:
        if not request.user.is_superuser:
            network = Network.objects.filter(
                memberships__user=request.user,
                memberships__role=NetworkMembership.Role.ADMIN,
            ).get(name=name)
        else:
            network = Network.objects.get(name=name)
        network.delete()
        return {"message": f"Network {name} deleted"}
    except Network.DoesNotExist:
        return HttpResponse(status=404, content=f"Network {name} not found")


@api.post("/templates", response=schemas.TemplateResponse, auth=keycloak_auth)
def create_template_endpoint(request: HttpRequest, data: schemas.TemplateCreate):
    try:
        network = Network.objects.get(name=data.network_name)
    except Network.DoesNotExist:
        return HttpResponse(
            status=404, content=f"Network {data.network_name} not found"
        )
    if not request.user.is_superuser:
        if not network.memberships.filter(
            user=request.user, role=NetworkMembership.Role.ADMIN
        ).exists():
            return HttpResponse(status=403, content="Permission denied")

    template = create_template(
        name=data.name,
        network_name=data.network_name,
        is_lighthouse=data.is_lighthouse,
        is_relay=data.is_relay,
        use_relay=data.use_relay,
    )
    return {
        "id": template.id,
        "name": template.name,
        "enrollment_key": template.enrollment_key,
    }


@api.delete("/templates/{name}", auth=keycloak_auth)
def delete_template(request: HttpRequest, name: str):
    try:
        if not request.user.is_superuser:
            template = Template.objects.filter(
                network__memberships__user=request.user,
                network__memberships__role=NetworkMembership.Role.ADMIN,
            ).get(name=name)
        else:
            template = Template.objects.get(name=name)
        template.delete()
        return {"message": f"Template {name} deleted"}
    except Template.DoesNotExist:
        return HttpResponse(status=404, content=f"Template {name} not found")


@api.get("/templates/{name}/token", auth=keycloak_auth)
def get_template_token(request: HttpRequest, name: str):
    try:
        if not request.user.is_superuser:
            template = Template.objects.filter(
                network__memberships__user=request.user,
                network__memberships__role=NetworkMembership.Role.ADMIN,
            ).get(name=name)
        else:
            template = Template.objects.get(name=name)
        return {
            "token": generate_enrollment_token(template),
            "template_id": template.id,
        }
    except Template.DoesNotExist:
        return HttpResponse(status=404, content=f"Template {name} not found")


@api.delete("/hosts/{name}", auth=keycloak_auth)
def delete_host(request: HttpRequest, name: str):
    try:
        if not request.user.is_superuser:
            host = Host.objects.filter(
                network__memberships__user=request.user,
                network__memberships__role=NetworkMembership.Role.ADMIN,
            ).get(name=name)
        else:
            host = Host.objects.get(name=name)
        host.delete()
        return {"message": f"Host {name} deleted"}
    except Host.DoesNotExist:
        return HttpResponse(status=404, content=f"Host {name} not found")


@api.get("/test")
def test(request: HttpRequest):
    return {"message": "Test endpoint"}
