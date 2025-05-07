import asyncio

import structlog
import typer

from meshadmin.cli.utils import perform_self_upgrade

system_app = typer.Typer(no_args_is_help=True)
logger = structlog.get_logger(__name__)


@system_app.command(name="upgrade")
def upgrade_command():
    logger.info("Starting manual meshadmin upgrade")
    result = asyncio.run(perform_self_upgrade())
    if not result:
        raise typer.Exit(code=1)
    logger.info("Manual meshadmin upgrade completed successfully")
