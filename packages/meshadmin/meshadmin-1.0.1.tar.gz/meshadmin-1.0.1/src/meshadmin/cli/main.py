from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from time import sleep
from typing import Annotated

import httpx
import jwt
import structlog
import typer
import yaml

from meshadmin.cli.commands import (
    context_app,
    host_app,
    nebula_app,
    network_app,
    service_app,
    system_app,
    template_app,
)
from meshadmin.cli.config import get_config, load_config, set_config
from meshadmin.common.utils import get_default_config_path

app = typer.Typer()
logger = structlog.get_logger(__name__)

app.add_typer(nebula_app, name="nebula", help="Manage the nebula service")
app.add_typer(service_app, name="service", help="Manage the meshadmin service")
app.add_typer(network_app, name="network", help="Manage networks")
app.add_typer(template_app, name="template", help="Manage templates")
app.add_typer(host_app, name="host", help="Manage hosts")
app.add_typer(context_app, name="context", help="Manage network contexts")
app.add_typer(system_app, name="system", help="System maintenance commands")


def version_callback(value: bool):
    if value:
        try:
            installed_version = version("meshadmin")
            typer.echo(f"meshadmin version {installed_version}")
        except PackageNotFoundError:
            typer.echo("meshadmin is not installed")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
    config_path: Annotated[
        Path,
        typer.Option(
            "--config-path",
            "-c",
            envvar="MESHADMIN_CONFIG_PATH",
            help="Path to the configuration directory",
        ),
    ] = get_default_config_path(),
    context: Annotated[
        str,
        typer.Option(
            "--context",
            envvar="MESH_CONTEXT",
            help="Name of the context to use",
        ),
    ] = None,
):
    config = load_config(config_path)
    set_config(config)

    if context:
        if not config.contexts_file.exists():
            print("No contexts found")
            raise typer.Exit(1)

        with open(config.contexts_file) as f:
            contexts = yaml.safe_load(f) or {}

        if context not in contexts:
            print(f"Context '{context}' not found")
            raise typer.Exit(1)

        for ctx_name in contexts:
            contexts[ctx_name]["active"] = ctx_name == context

        with open(config.contexts_file, "w") as f:
            yaml.dump(contexts, f)


@app.command()
def login():
    config = get_config()
    res = httpx.post(
        config.keycloak_device_auth_url,
        data={
            "client_id": config.keycloak_admin_client,
        },
    )
    res.raise_for_status()

    device_auth_response = res.json()
    print(device_auth_response)
    print(
        "Please open the verification url",
        device_auth_response["verification_uri_complete"],
    )

    while True:
        res = httpx.post(
            config.keycloak_token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": config.keycloak_admin_client,
                "device_code": device_auth_response["device_code"],
            },
        )
        if res.status_code == 200:
            logger.info("Received auth token")
            config.authentication_path.write_bytes(res.content)
            config.authentication_path.chmod(0o600)

            access_token = res.json()["access_token"]
            refresh_token = res.json()["refresh_token"]
            print(
                jwt.decode(
                    refresh_token,
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )
            )
            logger.info("access_token", access_token=access_token)
            print("successfully authenticated")
            break
        else:
            print(res.json())
        sleep(device_auth_response["interval"])


if __name__ == "__main__":
    app()
