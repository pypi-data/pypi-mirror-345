import asyncio
from pathlib import Path

import structlog
import typer

from meshadmin.cli.utils import get_context_config, start_nebula
from meshadmin.common.utils import download_nebula_binaries, get_nebula_path

nebula_app = typer.Typer()
logger = structlog.get_logger(__name__)


@nebula_app.command()
def download():
    try:
        context = get_context_config()
        nebula_path = get_nebula_path()
        if not nebula_path or not Path(nebula_path).exists():
            logger.info("Nebula binaries not found, downloading...")
            download_nebula_binaries(context["endpoint"])
        else:
            logger.info("Nebula binaries already downloaded")
    except Exception as e:
        logger.error("Failed to download nebula binaries", error=str(e))
        raise typer.Exit(code=1)


@nebula_app.command()
def start():
    context = get_context_config()
    asyncio.run(start_nebula(context["network_dir"], context["endpoint"]))
