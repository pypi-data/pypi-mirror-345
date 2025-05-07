import httpx
import structlog
import typer
from rich import print, print_json

from meshadmin.cli.utils import get_access_token, get_context_config
from meshadmin.common import schemas

template_app = typer.Typer()
logger = structlog.get_logger(__name__)


@template_app.command(name="create")
def create_template(
    name: str, network_name: str, is_lighthouse: bool, is_relay: bool, use_relay: bool
):
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.post(
        f"{context['endpoint']}/api/v1/templates",
        content=schemas.TemplateCreate(
            name=name,
            network_name=network_name,
            is_lighthouse=is_lighthouse,
            is_relay=is_relay,
            use_relay=use_relay,
        ).model_dump_json(),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    print_json(res.content.decode("utf-8"))


@template_app.command()
def get_token(name: str):
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.get(
        f"{context['endpoint']}/api/v1/templates/{name}/token",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    print_json(res.content.decode("utf-8"))


@template_app.command(name="delete")
def delete_template(name: str):
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.delete(
        f"{context['endpoint']}/api/v1/templates/{name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    print(res.json())
