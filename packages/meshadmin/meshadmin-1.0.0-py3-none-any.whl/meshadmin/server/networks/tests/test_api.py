import json
from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT

from meshadmin.common import schemas
from meshadmin.common.utils import create_keys
from meshadmin.server.networks.models import Host, Template
from meshadmin.server.networks.services import (
    create_template,
    generate_enrollment_token,
)


@pytest.fixture
def keycloak_key():
    key = JWK.generate(kty="RSA", size=2048, kid="test-key-id")
    return {
        "private_key": key,
        "public_key": json.loads(key.export_public()),
        "kid": "test-key-id",
    }


@pytest.fixture
def keycloak_auth_headers(mocker, keycloak_key, settings):
    jwt_token = JWT(
        header={"alg": "RS256", "kid": keycloak_key["kid"]},
        claims={
            "exp": 9999999999,
            "iat": 1741328648,
            "iss": settings.KEYCLOAK_ISSUER,
            "azp": settings.KEYCLOAK_ADMIN_CLIENT,
            "typ": "Bearer",
            "email": "test@example.com",
        },
    )
    jwt_token.make_signed_token(keycloak_key["private_key"])
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"keys": [keycloak_key["public_key"]]}
    mock_get.return_value.raise_for_status.return_value = None

    mocker.patch(
        "meshadmin.server.networks.api.KeycloakAuthBearer.get_keycloak_public_key",
        return_value={"keys": [keycloak_key["public_key"]]},
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {jwt_token.serialize()}"}


def test_template_endpoints(db, client, test_network, keycloak_auth_headers):
    network = test_network(name="test_network", cidr="100.100.64.0/24")
    template_data = schemas.TemplateCreate(
        name="test_template",
        network_name=network.name,
        is_lighthouse=True,
        is_relay=True,
        use_relay=False,
    )
    response = client.post(
        "/api/v1/templates",
        data=template_data.model_dump_json(),
        content_type="application/json",
        **keycloak_auth_headers,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "test_template"
    assert "enrollment_key" in response_data

    # Delete template
    response = client.delete(
        "/api/v1/templates/test_template",
        **keycloak_auth_headers,
    )
    assert response.status_code == 200
    assert not Template.objects.filter(name="test_template").exists()


def test_host_endpoints(client, test_network, keycloak_auth_headers):
    network = test_network(name="test_network", cidr="100.100.64.0/24")
    # First create and enroll a host
    template = create_template(
        "host_template",
        network.name,
        is_lighthouse=False,
        is_relay=False,
    )
    token = generate_enrollment_token(template)
    auth_key = JWK.generate(kty="RSA", size=2048)
    _, public_net_key = create_keys()
    enrollment_data = schemas.ClientEnrollment(
        enrollment_key=token,
        public_net_key=public_net_key,
        public_auth_key=auth_key.export_public(),
        preferred_hostname="test-host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )
    response = client.post(
        "/api/v1/enroll",
        data=enrollment_data.model_dump_json(),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Delete host
    response = client.delete(
        "/api/v1/hosts/test-host",
        **keycloak_auth_headers,
    )
    assert response.status_code == 200
    assert not Host.objects.filter(name="test-host").exists()


def test_unauthorized_access(db, client):
    endpoints = [
        ("POST", "/api/v1/networks"),
        ("GET", "/api/v1/networks"),
        ("DELETE", "/api/v1/networks/test"),
        ("POST", "/api/v1/templates"),
        ("DELETE", "/api/v1/templates/test"),
        ("DELETE", "/api/v1/hosts/test"),
    ]

    for method, endpoint in endpoints:
        if method == "POST":
            response = client.post(
                endpoint,
                data="{}",
                content_type="application/json",
            )
        else:
            response = (
                client.get(endpoint) if method == "GET" else client.delete(endpoint)
            )
        assert response.status_code == 401, f"{method} {endpoint} should require auth"


def test_wrong_client_id(db, client, keycloak_key, settings):
    jwt_token = JWT(
        header={"alg": "RS256", "kid": keycloak_key["kid"]},
        claims={
            "exp": 9999999999,
            "iat": 1741328648,
            "iss": settings.KEYCLOAK_ISSUER,
            "azp": "wrong-client",  # Not admin-cli
            "typ": "Bearer",
        },
    )
    jwt_token.make_signed_token(keycloak_key["private_key"])
    headers = {"HTTP_AUTHORIZATION": f"Bearer {jwt_token.serialize()}"}
    response = client.get("/api/v1/networks", **headers)
    assert response.status_code == 401


def test_wrong_signature(db, client, keycloak_key, mocker):
    different_key = JWK.generate(kty="RSA", size=2048)
    jwt_token = JWT(
        header={"alg": "RS256", "kid": keycloak_key["kid"]},
        claims={
            "exp": 9999999999,
            "iat": 1741328648,
            "iss": "http://localhost:8080/realms/meshadmin",
            "azp": "admin-cli",
            "typ": "Bearer",
        },
    )
    jwt_token.make_signed_token(different_key)
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"keys": [keycloak_key["public_key"]]}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.get", return_value=mock_response)
    headers = {"HTTP_AUTHORIZATION": f"Bearer {jwt_token.serialize()}"}
    response = client.get("/api/v1/networks", **headers)
    assert response.status_code == 401


def test_get_config(db, client, test_network):
    network = test_network(name="test_network", cidr="10.0.0.0/24")
    auth_key = JWK.generate(kty="RSA", size=2048)
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    host = Host.objects.create(
        network=network,
        name="test-host",
        assigned_ip="10.0.0.1",
        public_key=public_key,
        public_auth_key=public_auth_key,
        public_auth_kid=auth_key.thumbprint(),
    )
    jwt_token = JWT(
        header={"alg": "RS256", "kid": auth_key.thumbprint()},
        claims={
            "exp": 9999999999,
            "kid": auth_key.thumbprint(),
        },
    )
    jwt_token.make_signed_token(auth_key)
    host_auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {jwt_token.serialize()}"}
    response = client.get(
        "/api/v1/config",
        **host_auth_headers,
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "text/yaml"
    host.refresh_from_db()
    assert host.last_config_refresh is not None
    assert host.last_config_refresh > timezone.now() - timedelta(minutes=1)


def test_cleanup_ephemeral_hosts(db, client, test_network):
    network = test_network(name="test_network", cidr="10.0.0.0/24")
    auth_key = JWK.generate(kty="RSA", size=2048)
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    Host.objects.create(
        network=network,
        name="requesting-host",
        assigned_ip="10.0.0.10",
        public_key=public_key,
        public_auth_key=public_auth_key,
        public_auth_kid=auth_key.thumbprint(),
    )
    jwt_token = JWT(
        header={"alg": "RS256", "kid": auth_key.thumbprint()},
        claims={
            "exp": 9999999999,
            "kid": auth_key.thumbprint(),
        },
    )
    jwt_token.make_signed_token(auth_key)
    host_auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {jwt_token.serialize()}"}

    # Create some ephemeral hosts
    # 1. A stale host (last_config_refresh > 10 minutes ago)
    stale_host = Host.objects.create(
        network=network,
        name="stale-host",
        assigned_ip="10.0.0.1",
        public_key="test-key-1",
        public_auth_key="{}",
        public_auth_kid="test-kid-1",
        is_ephemeral=True,
        last_config_refresh=timezone.now() - timedelta(minutes=15),
    )

    # 2. A recently seen ephemeral host (should not be removed)
    recent_host = Host.objects.create(
        network=network,
        name="recent-host",
        assigned_ip="10.0.0.2",
        public_key="test-key-2",
        public_auth_key="{}",
        public_auth_kid="test-kid-2",
        is_ephemeral=True,
        last_config_refresh=timezone.now() - timedelta(minutes=5),
    )

    # 3. A non-ephemeral host (should not be removed regardless of last_config_refresh)
    non_ephemeral_host = Host.objects.create(
        network=network,
        name="non-ephemeral-host",
        assigned_ip="10.0.0.3",
        public_key="test-key-3",
        public_auth_key="{}",
        public_auth_kid="test-kid-3",
        is_ephemeral=False,
        last_config_refresh=timezone.now() - timedelta(minutes=30),
    )

    response = client.post(
        "/api/v1/cleanup-ephemeral",
        **host_auth_headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["removed_count"] == 1
    assert not Host.objects.filter(id=stale_host.id).exists()
    assert Host.objects.filter(id=recent_host.id).exists()
    assert Host.objects.filter(id=non_ephemeral_host.id).exists()

    # Call the endpoint again - should remove no hosts
    response = client.post(
        "/api/v1/cleanup-ephemeral",
        **host_auth_headers,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["removed_count"] == 0


def test_enrollment_api_with_jwt(test_network, client):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "jwt_template",
        network.name,
    )
    token = generate_enrollment_token(template)
    auth_key = JWK.generate(kty="RSA", size=2048)
    _, public_net_key = create_keys()
    enrollment_data = schemas.ClientEnrollment(
        enrollment_key=token,
        public_net_key=public_net_key,
        public_auth_key=auth_key.export_public(),
        preferred_hostname="test-host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )
    response = client.post(
        "/api/v1/enroll",
        data=enrollment_data.model_dump_json(),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert Host.objects.filter(name="test-host").exists()


def test_download_nebula_binary(client, mocker):
    mock_content = b"mock binary content"
    mock_file = mocker.mock_open(read_data=mock_content)
    mocker.patch("builtins.open", mock_file)
    mocker.patch("meshadmin.server.assets.asset_path")
    mocker.patch.object(Path, "exists", return_value=True)

    # Test valid download for Linux (x86_64)
    response = client.get("/api/v1/nebula/download/Linux/x86_64/nebula")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/octet-stream"
    assert response["Content-Disposition"] == 'attachment; filename="nebula"'
    content = b"".join(response.streaming_content)
    assert content == mock_content

    # Test valid download for Linux (aarch64)
    response = client.get("/api/v1/nebula/download/Linux/aarch64/nebula")
    assert response.status_code == 200

    # Test valid download for Darwin (arm64)
    response = client.get("/api/v1/nebula/download/Darwin/arm64/nebula-cert")
    assert response.status_code == 200

    # Test invalid OS
    response = client.get("/api/v1/nebula/download/Windows/x86_64/nebula")
    assert response.status_code == 400
    assert "Only Linux and Darwin are supported" in str(response.content)

    # Test invalid architecture for Darwin
    response = client.get("/api/v1/nebula/download/Darwin/x86_64/nebula")
    assert response.status_code == 400
    assert "Supported architectures for Darwin: ['arm64']" in str(response.content)

    # Test invalid architecture for Linux
    response = client.get("/api/v1/nebula/download/Linux/arm64/nebula")
    assert response.status_code == 400
    assert "Supported architectures for Linux: ['aarch64', 'x86_64']" in str(
        response.content
    )

    # Test invalid binary name
    response = client.get("/api/v1/nebula/download/Linux/x86_64/invalid")
    assert response.status_code == 400

    # Test binary not found
    mocker.patch.object(Path, "exists", return_value=False)
    response = client.get("/api/v1/nebula/download/Linux/x86_64/nebula")
    assert response.status_code == 404
    assert "Binary not found" in str(response.content)
