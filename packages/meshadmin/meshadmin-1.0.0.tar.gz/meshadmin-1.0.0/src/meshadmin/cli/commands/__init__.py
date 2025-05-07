from meshadmin.cli.commands.context import context_app
from meshadmin.cli.commands.host import host_app
from meshadmin.cli.commands.nebula import nebula_app
from meshadmin.cli.commands.network import network_app
from meshadmin.cli.commands.service import service_app
from meshadmin.cli.commands.system import system_app
from meshadmin.cli.commands.template import template_app

__all__ = [
    "nebula_app",
    "service_app",
    "network_app",
    "template_app",
    "host_app",
    "context_app",
    "system_app",
]
