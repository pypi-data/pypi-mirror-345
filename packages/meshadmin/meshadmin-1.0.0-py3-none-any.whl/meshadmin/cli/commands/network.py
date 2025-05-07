import httpx
import structlog
import typer
from rich import print, print_json

from meshadmin.cli.utils import get_access_token, get_context_config
from meshadmin.common import schemas

network_app = typer.Typer()
logger = structlog.get_logger(__name__)


@network_app.command(name="create")
def create_network(name: str, cidr: str):
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.post(
        f"{context['endpoint']}/api/v1/networks",
        content=schemas.NetworkCreate(name=name, cidr=cidr).model_dump_json(),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if res.status_code >= 400:
        print("could not create network:", res.text)
        exit(1)

    print_json(res.content.decode("utf-8"))


@network_app.command(name="list")
def list_networks():
    try:
        access_token = get_access_token()
    except Exception:
        logger.exception("failed to get access token")
        exit(1)

    context = get_context_config()
    res = httpx.get(
        f"{context['endpoint']}/api/v1/networks",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    print(res.json())
