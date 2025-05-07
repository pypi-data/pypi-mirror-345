import asyncio
import os
import platform
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import httpx
import structlog
import typer
from jwcrypto.jwk import JWK

from meshadmin.cli.commands.nebula import download
from meshadmin.cli.config import get_config
from meshadmin.cli.utils import (
    get_access_token,
    get_config_from_mesh,
    get_context_config,
)
from meshadmin.common import schemas
from meshadmin.common.utils import create_keys, get_default_config_path, get_public_ip

host_app = typer.Typer()
logger = structlog.get_logger(__name__)

host_config_app = typer.Typer()
host_app.add_typer(host_config_app, name="config", help="Manage host configurations")


@host_app.command(name="enroll")
def host_enroll(
    enrollment_key: Annotated[
        str,
        typer.Argument(envvar="MESH_ENROLLMENT_KEY"),
    ],
    preferred_hostname: Annotated[
        str,
        typer.Option(envvar="MESH_HOSTNAME"),
    ] = None,
    public_ip: Annotated[
        str,
        typer.Option(envvar="MESH_PUBLIC_IP"),
    ] = None,
):
    config = get_config()
    context = get_context_config()
    network_dir = context["network_dir"]

    download()
    logger.info("enrolling")

    network_dir.mkdir(parents=True, exist_ok=True)

    # Use shared auth key for all contexts
    private_auth_key_path = config.contexts_file.parent / config.private_key
    if not private_auth_key_path.exists():
        logger.info("creating auth key")
        create_auth_key(private_auth_key_path.parent)

    jwk = JWK.from_json(private_auth_key_path.read_text())
    public_auth_key = jwk.export_public()
    logger.info("public key for registration", public_key=public_auth_key)

    private_net_key_path = network_dir / config.private_net_key_file
    public_net_key_path = network_dir / config.public_net_key_file

    if public_ip is None:
        public_ip = get_public_ip()
        logger.info(
            "public ip not set, using ip reported by https://checkip.amazonaws.com/",
            public_ip=public_ip,
        )

    if preferred_hostname is None:
        preferred_hostname = platform.node()
        logger.info(
            "preferred hostname not set, using system hostname",
            hostname=preferred_hostname,
        )

    if private_net_key_path.exists() and public_net_key_path.exists():
        public_nebula_key = public_net_key_path.read_text()
        logger.info(
            "private and public nebula key already exists",
            public_key=public_nebula_key,
        )
    else:
        logger.info("creating private and public nebula key")
        private, public_nebula_key = create_keys()
        private_net_key_path.write_text(private)
        private_auth_key_path.chmod(0o600)
        public_net_key_path.write_text(public_nebula_key)
        public_net_key_path.chmod(0o600)
        logger.info(
            "private and public nebula key created", public_nebula_key=public_nebula_key
        )

    enrollment = schemas.ClientEnrollment(
        enrollment_key=enrollment_key,
        public_net_key=public_nebula_key,
        public_auth_key=public_auth_key,
        preferred_hostname=preferred_hostname,
        public_ip=public_ip,
        interface=context["interface"],
    )

    res = httpx.post(
        f"{context['endpoint']}/api/v1/enroll",
        content=enrollment.model_dump_json(),
        headers={"Content-Type": "application/json"},
    )
    res.raise_for_status()

    get_host_config()
    logger.info("enrollment response", enrollment=res.content)
    logger.info("enrollment finished")


@host_app.command()
def create_auth_key(
    mesh_config_path: Annotated[
        Path,
        typer.Argument(envvar="MESH_CONFIG_PATH"),
    ] = get_default_config_path(),
):
    config = get_config()
    jwk = JWK.generate(kty="RSA", kid=str(uuid4()), size=2048)
    auth_key = mesh_config_path / config.private_key
    auth_key.write_text(jwk.export_private())
    auth_key.chmod(0o600)


@host_app.command()
def show_auth_public_key(
    mesh_config_path: Annotated[
        Path,
        typer.Argument(envvar="MESH_CONFIG_PATH"),
    ] = get_default_config_path(),
):
    config = get_config()
    jwk = JWK.from_json((mesh_config_path / config.private_key).read_text())
    print(jwk.export_public())


@host_config_app.command()
def get_host_config():
    config = get_config()
    private_net_key, public_net_key = create_keys()
    context = get_context_config()
    private_auth_key = JWK.from_json(
        (config.contexts_file.parent / config.private_key).read_text()
    )

    loop = asyncio.get_event_loop()

    result, _, _ = loop.run_until_complete(
        get_config_from_mesh(context["endpoint"], private_auth_key)
    )
    (context["network_dir"] / config.config_path).write_text(result)


@host_app.command(name="delete")
def delete_host(name: str):
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.delete(
        f"{context['endpoint']}/api/v1/hosts/{name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    print(res.json())


@host_config_app.command(name="info")
def show_config_info():
    config = get_config()
    print("\nConfiguration Paths:")
    print(f"Contexts file: {config.contexts_file}")
    print(f"Networks directory: {config.networks_dir}")
    try:
        context = get_context_config()
        print("\nCurrent Context:")
        print(f"Name: {context['name']}")
        print(f"Endpoint: {context['endpoint']}")
        print(f"Interface: {context['interface']}")
        print(f"Network directory: {context['network_dir']}")

        config_file = context["network_dir"] / config.config_path
        env_file = context["network_dir"] / "env"
        private_key = context["network_dir"] / config.private_net_key_file

        print("\nContext Files:")
        print(
            f"Config file: {config_file} {'(exists)' if config_file.exists() else '(not found)'}"
        )
        print(
            f"Environment file: {env_file} {'(exists)' if env_file.exists() else '(not found)'}"
        )
        print(
            f"Private key: {private_key} {'(exists)' if private_key.exists() else '(not found)'}"
        )
        if platform.system() == "Darwin":
            service_file = Path(
                os.path.expanduser(
                    f"~/Library/LaunchAgents/com.meshadmin.{context['name']}.plist"
                )
            )
            print(
                f"Service file: {service_file} {'(exists)' if service_file.exists() else '(not found)'}"
            )
        else:
            service_file = Path(
                f"/usr/lib/systemd/system/meshadmin-{context['name']}.service"
            )
            print(
                f"Service file: {service_file} {'(exists)' if service_file.exists() else '(not found)'}"
            )
    except typer.Exit:
        print("\nNo active context found")
