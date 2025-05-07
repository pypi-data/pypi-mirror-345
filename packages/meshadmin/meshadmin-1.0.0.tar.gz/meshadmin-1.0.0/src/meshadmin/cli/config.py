import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NetworkContext:
    name: str
    endpoint: str
    interface: str = "nebula1"
    active: bool = False


@dataclass
class MeshConfig:
    keycloak_base_url: str
    keycloak_realm: str
    keycloak_admin_client: str
    keycloak_issuer: str
    keycloak_device_auth_url: str
    keycloak_token_url: str
    private_key: Path
    private_net_key_file: Path
    public_net_key_file: Path
    config_path: Path
    authentication_path: Path
    contexts_file: Path
    networks_dir: Path


def load_config(base_config_path: Path):
    KEYCLOAK_BASE_URL = os.getenv(
        "KEYCLOAK_BASE_URL", "https://auth.dmeshadmin.hydo.ch"
    )
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "meshadmin")
    KEYCLOAK_ADMIN_CLIENT = os.getenv("KEYCLOAK_ADMIN_CLIENT", "admin-cli")
    KEYCLOAK_ISSUER = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}"
    KEYCLOAK_DEVICE_AUTH_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/auth/device"
    KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"

    return MeshConfig(
        keycloak_base_url=KEYCLOAK_BASE_URL,
        keycloak_realm=KEYCLOAK_REALM,
        keycloak_admin_client=KEYCLOAK_ADMIN_CLIENT,
        keycloak_issuer=KEYCLOAK_ISSUER,
        keycloak_device_auth_url=KEYCLOAK_DEVICE_AUTH_URL,
        keycloak_token_url=KEYCLOAK_TOKEN_URL,
        private_key=Path("auth.key"),
        private_net_key_file=Path("host.key"),
        public_net_key_file=Path("host.pub"),
        config_path=Path("config.yaml"),
        authentication_path=Path("auth.json"),
        contexts_file=base_config_path / "contexts.yaml",
        networks_dir=base_config_path / "networks",
    )


_config = None


def get_config():
    global _config
    return _config


def set_config(config: MeshConfig):
    global _config
    _config = config
