import asyncio
import json
import os
import signal
from datetime import datetime, timedelta
from importlib.metadata import version
from pathlib import Path

import httpx
import structlog
import typer
import yaml
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from jwt import decode

from meshadmin.cli.config import get_config
from meshadmin.common.utils import create_expiration_date, get_nebula_path

logger = structlog.get_logger(__name__)


def get_access_token():
    if os.getenv("MESHADMIN_TEST_MODE") == "true":
        return "test-token"

    config = get_config()
    if config.authentication_path.exists():
        auth = json.loads(config.authentication_path.read_text())
        access_token = auth["access_token"]

        decoded_token = decode(
            access_token, options={"verify_signature": False, "verify_exp": False}
        )

        # is exp still 2/3 of the time
        if decoded_token["exp"] >= (datetime.now() + timedelta(seconds=10)).timestamp():
            return access_token
        else:
            refresh_token = auth["refresh_token"]
            res = httpx.post(
                config.keycloak_token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": config.keycloak_admin_client,
                },
            )
            res.raise_for_status()
            config.authentication_path.write_bytes(res.content)
            return res.json()["access_token"]

    else:
        print("authentication failed")


def get_context_config():
    config = get_config()
    if not config.contexts_file.exists():
        print("No contexts found")
        raise typer.Exit(1)

    with open(config.contexts_file) as f:
        contexts = yaml.safe_load(f) or {}

    current = os.getenv("MESH_CONTEXT")
    if not current:
        active_contexts = [
            name for name, data in contexts.items() if data.get("active")
        ]
        current = active_contexts[0] if active_contexts else None

    if not current or current not in contexts:
        print("No active context. Please select a context with 'meshadmin context use'")
        raise typer.Exit(1)

    context_data = contexts[current]
    network_dir = config.networks_dir / current

    return {
        "name": current,
        "endpoint": context_data["endpoint"],
        "interface": context_data["interface"],
        "network_dir": network_dir,
    }


async def get_config_from_mesh(mesh_admin_endpoint, private_auth_key):
    jwt = JWT(
        header={"alg": "RS256", "kid": private_auth_key.thumbprint()},
        claims={
            "exp": create_expiration_date(10),
            "kid": private_auth_key.thumbprint(),
        },
    )
    jwt.make_signed_token(private_auth_key)
    token = jwt.serialize()

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{mesh_admin_endpoint}/api/v1/config",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Meshadmin-Version": version("meshadmin"),
            },
        )
        res.raise_for_status()
        config = res.text
        update_interval = int(res.headers.get("X-Update-Interval", "5"))
        upgrade_required = res.headers.get("X-Upgrade-Requested") == "true"
        return config, update_interval, upgrade_required


async def cleanup_ephemeral_hosts(mesh_admin_endpoint, private_auth_key):
    jwt_token = JWT(
        header={"alg": "RS256", "kid": private_auth_key.thumbprint()},
        claims={
            "exp": create_expiration_date(10),
            "kid": private_auth_key.thumbprint(),
        },
    )
    jwt_token.make_signed_token(private_auth_key)
    token = jwt_token.serialize()

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{mesh_admin_endpoint}/api/v1/cleanup-ephemeral",
            headers={"Authorization": f"Bearer {token}"},
        )
        res.raise_for_status()
        return res.json()


async def start_nebula(network_dir: Path, mesh_admin_endpoint: str):
    config = get_config()
    await logger.ainfo("starting nebula")
    conf_path = network_dir / config.config_path
    assert conf_path.exists(), f"Config at {conf_path} does not exist"

    private_auth_key_path = config.contexts_file.parent / config.private_key
    assert private_auth_key_path.exists(), (
        f"private_key at {private_auth_key_path} does not exist"
    )

    async def start_process():
        return await asyncio.create_subprocess_exec(
            get_nebula_path(),
            "-config",
            str(conf_path),
            cwd=network_dir,
        )

    proc = await start_process()

    # Default update interval in seconds
    update_interval = 5

    while True:
        await asyncio.sleep(update_interval)
        try:
            private_auth_key_path = config.contexts_file.parent / config.private_key
            private_auth_key = JWK.from_json(private_auth_key_path.read_text())

            # Check for config updates
            try:
                (
                    new_config,
                    new_update_interval,
                    upgrade_required,
                ) = await get_config_from_mesh(mesh_admin_endpoint, private_auth_key)
                if upgrade_required:
                    await logger.ainfo("Starting meshadmin self-upgrade")
                    await perform_self_upgrade()

                if update_interval != new_update_interval:
                    await logger.ainfo(
                        "update interval changed",
                        old_interval=update_interval,
                        new_interval=new_update_interval,
                    )
                    update_interval = new_update_interval

                old_config = conf_path.read_text()
                if new_config != old_config:
                    await logger.ainfo("config changed, reloading")
                    conf_path.write_text(new_config)
                    conf_path.chmod(0o600)

                    try:
                        proc.send_signal(signal.SIGHUP)
                    except ProcessLookupError:
                        await logger.ainfo("process died, restarting")
                        proc = await start_process()
                else:
                    await logger.ainfo("config not changed")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    await logger.aerror(
                        "Could not get config because of authentication error. Host may have been deleted.",
                        error=str(e),
                        response_text=e.response.text,
                    )
                    print(
                        "Error: Could not get config because of authentication error. Host may have been deleted."
                    )
                    print(f"Server message: {e.response.text}")
                    break
                else:
                    await logger.aerror("error getting config", error=str(e))

            # Cleanup ephemeral hosts
            try:
                result = await cleanup_ephemeral_hosts(
                    mesh_admin_endpoint, private_auth_key
                )
                if result.get("removed_count", 0) > 0:
                    await logger.ainfo(
                        "removed stale ephemeral hosts",
                        count=result["removed_count"],
                    )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    await logger.aerror(
                        "Could not clean up ephemeral hosts because of authentication error. Host may have been deleted.",
                        error=str(e),
                        response_text=e.response.text,
                    )
                    print(
                        "Error: Could not clean up ephemeral hosts because of authentication error. Host may have been deleted."
                    )
                    print(f"Server message: {e.response.text}")
                    break
                else:
                    await logger.aerror("error during cleanup operation", error=str(e))

        except Exception:
            await logger.aexception("could not refresh token")
            if proc.returncode is not None:
                await logger.ainfo("process died, restarting")
                proc = await start_process()

    # Clean shutdown if we get here
    if proc.returncode is None:
        await logger.ainfo("shutting down nebula process")
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            await logger.awarning("nebula process didn't terminate, killing it")
            proc.kill()


async def perform_self_upgrade():
    try:
        process = await asyncio.create_subprocess_exec(
            "uv",
            "tool",
            "install",
            "--upgrade",
            "meshadmin",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            await logger.ainfo(
                "meshadmin successfully upgraded",
                stdout=stdout.decode().strip() if stdout else None,
            )
            return True
        else:
            await logger.aerror(
                "meshadmin upgrade failed",
                returncode=process.returncode,
                stderr=stderr.decode().strip() if stderr else None,
            )
            return False
    except Exception as e:
        await logger.aerror("Error during meshadmin self-upgrade", error=str(e))
        return False
