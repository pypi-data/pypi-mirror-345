from typing import Annotated

import structlog
import typer
import yaml

from meshadmin.cli.config import get_config

context_app = typer.Typer()
logger = structlog.get_logger(__name__)


@context_app.command(name="create")
def create_context(
    name: Annotated[str, typer.Argument()],
    endpoint: Annotated[str, typer.Option()],
    interface: Annotated[str, typer.Option()] = "nebula1",
):
    config = get_config()
    config.contexts_file.parent.mkdir(parents=True, exist_ok=True)

    contexts = {}
    if config.contexts_file.exists():
        with open(config.contexts_file) as f:
            contexts = yaml.safe_load(f) or {}

    # If this is the first context, make it active
    is_first = len(contexts) == 0

    contexts[name] = {
        "endpoint": endpoint,
        "interface": interface,
        "active": is_first,
    }

    with open(config.contexts_file, "w") as f:
        yaml.dump(contexts, f)

    print(f"Created context '{name}'")
    if is_first:
        print(f"Set '{name}' as active context")


@context_app.command(name="use")
def use_context(name: str):
    config = get_config()
    if not config.contexts_file.exists():
        print("No contexts found")
        raise typer.Exit(1)

    with open(config.contexts_file) as f:
        contexts = yaml.safe_load(f) or {}

    if name not in contexts:
        print(f"Context '{name}' not found")
        raise typer.Exit(1)

    # Deactivate all contexts and activate the selected one
    for context_name in contexts:
        contexts[context_name]["active"] = False
    contexts[name]["active"] = True

    with open(config.contexts_file, "w") as f:
        yaml.dump(contexts, f)

    print(f"Switched to context '{name}'")


@context_app.command(name="list")
def list_contexts():
    config = get_config()
    if not config.contexts_file.exists():
        print("No contexts found")
        return

    with open(config.contexts_file) as f:
        contexts = yaml.safe_load(f)

    for name, data in contexts.items():
        print(
            f"{'* ' if data.get('active') else '  '}{name} ({data['endpoint']}) ({data['interface']})"
        )
