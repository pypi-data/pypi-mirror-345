import json
import os
import platform
import stat
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import structlog

logger = structlog.get_logger(__name__)


def get_nebula_install_path():
    os_name = platform.system()

    if os_name == "Darwin":
        base_path = Path(os.path.expanduser("~/Library/Application Support/nebula"))
    elif os_name == "Linux":
        base_path = Path("/opt/nebula")
    else:
        raise NotImplementedError(f"Unsupported operating system: {os_name}")

    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)

    return base_path


def download_nebula_binaries(mesh_admin_endpoint):
    os_name = platform.system()
    if os_name not in ["Linux", "Darwin"]:
        raise NotImplementedError(
            f"Unsupported operating system: {os_name}. Only Linux and Darwin are supported."
        )

    architecture = platform.machine()

    binaries = ["nebula", "nebula-cert"]
    install_path = get_nebula_install_path()

    for binary in binaries:
        binary_path = install_path / binary

        if binary_path.exists():
            logger.info(f"{binary} binary already exists", path=str(binary_path))
            continue

        url = f"{mesh_admin_endpoint}/api/v1/nebula/download/{os_name}/{architecture}/{binary}"
        logger.info(f"Downloading {binary}", url=url)

        try:
            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                with open(binary_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            # Make the binary executable
            binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)
            logger.info(f"{binary} downloaded and installed", path=str(binary_path))

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to download {binary}", status_code=e.response.status_code
            )
            raise RuntimeError(f"Failed to download {binary}: {e}")

    return install_path


def get_nebula_path():
    return get_nebula_binary_path()


def get_nebula_binary_path():
    install_path = get_nebula_install_path()
    return install_path / "nebula"


def get_nebula_cert_binary_path():
    install_path = get_nebula_install_path()
    return install_path / "nebula-cert"


def create_keys():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = subprocess.run(
            [
                get_nebula_cert_binary_path(),
                "keygen",
                "-out-key",
                "private.key",
                "-out-pub",
                "public.key",
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Failed to create keys: {res.stderr}")

        private_key = (Path(tmpdir) / "private.key").read_text()
        public_key = (Path(tmpdir) / "public.key").read_text()

    return private_key, public_key


def sign_keys(
    ca_key: str,
    ca_crt: str,
    public_key: str,
    name: str,
    ip: str,
    groups: frozenset[str],
):
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        ca_crt_path = temp_path / "ca.crt"
        ca_crt_path.write_text(ca_crt)
        ca_key_path = temp_path / "ca.key"
        ca_key_path.write_text(ca_key)

        public_key_file = temp_path / "public.key"
        public_key_file.write_text(public_key)

        command = [
            str(get_nebula_cert_binary_path()),
            "sign",
            "-in-pub",
            "public.key",
            "-name",
            name,
            "-ip",
            ip,
            "-groups",
            " " + ",".join(groups) + " ",
            "-out-crt",
            "public.crt",
        ]
        print(f"cd {temp_path}")
        print(" ".join(command))

        res = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert res.returncode == 0, res.stderr
        cert = (Path(tmpdir) / "public.crt").read_text()
    return cert


def print_ca(cert: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        cert_path = temp_path / "cert.crt"
        cert_path.write_text(cert)

        command = [
            get_nebula_cert_binary_path(),
            "print",
            "-path",
            "cert.crt",
            "-json",
        ]
        res = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )

        assert res.returncode == 0, res.stderr
        output = res.stdout
        json_output = json.loads(output)
        return json_output


def create_ca(ca_name):
    with tempfile.TemporaryDirectory() as tmpdir:
        res = subprocess.run(
            [str(get_nebula_cert_binary_path()), "ca", "-name", ca_name],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        assert res.returncode == 0
        cert = (Path(tmpdir) / "ca.crt").read_text()
        key = (Path(tmpdir) / "ca.key").read_text()

    return cert, key


def create_expiration_date(minutes=60) -> int:
    return int(
        (
            datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(minutes)
        ).timestamp()
    )


def get_public_ip():
    res = httpx.get("https://checkip.amazonaws.com/")
    assert res.status_code == 200
    public_ip = res.text.strip()
    return public_ip


def get_default_config_path() -> Path:
    os_name = platform.system()
    if os_name == "Darwin":
        return Path(os.path.expanduser("~/Library/Application Support/meshadmin"))
    else:
        return Path("/etc/meshadmin")
