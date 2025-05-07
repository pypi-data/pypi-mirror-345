import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import structlog
import typer

from meshadmin.cli.utils import get_context_config

service_app = typer.Typer()
logger = structlog.get_logger(__name__)


@service_app.command(name="install")
def service_install():
    context = get_context_config()
    network_dir = context["network_dir"]
    context_name = context["name"]
    os_name = platform.system()
    meshadmin_path = shutil.which("meshadmin")

    if not meshadmin_path:
        logger.error("meshadmin executable not found in PATH")
        exit(1)

    (network_dir / "env").write_text(f"MESH_CONTEXT={context_name}\n")

    if os_name == "Darwin":
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.meshadmin.{context_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{meshadmin_path}</string>
        <string>nebula</string>
        <string>start</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>MESH_CONTEXT</key>
        <string>{context_name}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>{network_dir}/error.log</string>
    <key>StandardOutPath</key>
    <string>{network_dir}/output.log</string>
</dict>
</plist>
"""
        launch_agents_dir = Path(os.path.expanduser("~/Library/LaunchAgents"))
        if not launch_agents_dir.exists():
            launch_agents_dir.mkdir(exist_ok=True, parents=True)
        plist_path = launch_agents_dir / f"com.meshadmin.{context_name}.plist"
        plist_path.write_text(plist_content)
        subprocess.run(["launchctl", "load", str(plist_path)])
        logger.info(
            "meshadmin service installed and started",
            plist_path=str(plist_path),
            context_name=context_name,
        )
        print(f"meshadmin service installed at {plist_path}")
        print(f"Context: {context_name}")
        print("Service has been loaded and will start automatically on login")

    else:
        systemd_unit = f"""[Unit]
Description=Meshadmin {context_name}
Wants=basic.target network-online.target nss-lookup.target time-sync.target
After=basic.target network.target network-online.target
Before=sshd.service

[Service]
#Type=notify
#NotifyAccess=main
SyslogIdentifier={context_name}
EnvironmentFile={network_dir}/env
ExecReload=/bin/kill -HUP $MAINPID
ExecStart={meshadmin_path} nebula start
Restart=always

[Install]
WantedBy=multi-user.target
"""
        systemd_service_path = Path(
            f"/usr/lib/systemd/system/meshadmin-{context_name}.service"
        )
        systemd_service_path.write_text(systemd_unit)
        subprocess.run(["systemctl", "daemon-reload"])
        subprocess.run(["systemctl", "enable", f"meshadmin-{context_name}"])
        print(f"meshadmin service installed at {systemd_service_path}")
        print(f"Context: {context_name}")
        print("Service has been enabled and will start automatically on boot")


@service_app.command(name="uninstall")
def service_uninstall():
    context = get_context_config()
    context_name = context["name"]
    network_dir = context["network_dir"]
    os_name = platform.system()

    if os_name == "Darwin":
        plist_path = Path(
            os.path.expanduser(
                f"~/Library/LaunchAgents/com.meshadmin.{context_name}.plist"
            )
        )
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)])
            plist_path.unlink()
            env_path = network_dir / "env"
            if env_path.exists():
                env_path.unlink()
            logger.info("meshadmin service uninstalled", plist_path=str(plist_path))
            print(f"meshadmin service uninstalled from {plist_path}")
        else:
            logger.warning("meshadmin service not found", plist_path=str(plist_path))
            print("meshadmin service not found, nothing to uninstall")
    else:
        systemd_service_path = Path(
            f"/usr/lib/systemd/system/meshadmin-{context_name}.service"
        )
        if systemd_service_path.exists():
            subprocess.run(["systemctl", "stop", f"meshadmin-{context_name}"])
            subprocess.run(["systemctl", "disable", f"meshadmin-{context_name}"])
            subprocess.run(["systemctl", "daemon-reload"])
            systemd_service_path.unlink()
            env_path = network_dir / "env"
            if env_path.exists():
                env_path.unlink()
            logger.info("meshadmin service uninstalled")
            print("meshadmin service uninstalled")
        else:
            logger.warning("meshadmin service not found")
            print("meshadmin service not found, nothing to uninstall")


@service_app.command(name="start")
def service_start():
    context = get_context_config()
    context_name = context["name"]
    os_name = platform.system()

    if os_name == "Darwin":
        plist_path = Path(
            os.path.expanduser(
                f"~/Library/LaunchAgents/com.meshadmin.{context_name}.plist"
            )
        )
        if plist_path.exists():
            subprocess.run(["launchctl", "load", str(plist_path)])
            logger.info("meshadmin service started", context=context_name)
            print(f"meshadmin service started for context {context_name}")
        else:
            logger.error("meshadmin service not installed", plist_path=str(plist_path))
            print(
                f"meshadmin service not installed for context {context_name}. Run 'meshadmin service install' first."
            )
    else:
        subprocess.run(["systemctl", "start", f"meshadmin-{context_name}"])
        print(f"meshadmin service started for context {context_name}")


@service_app.command(name="stop")
def service_stop():
    context = get_context_config()
    context_name = context["name"]
    os_name = platform.system()

    if os_name == "Darwin":
        plist_path = Path(
            os.path.expanduser(
                f"~/Library/LaunchAgents/com.meshadmin.{context_name}.plist"
            )
        )
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)])
            logger.info("meshadmin service stopped", context=context_name)
            print(f"meshadmin service stopped for context {context_name}")
        else:
            logger.error("meshadmin service not installed", plist_path=str(plist_path))
            print(
                f"meshadmin service not installed for context {context_name}. Nothing to stop."
            )
    else:
        subprocess.run(["systemctl", "stop", f"meshadmin-{context_name}"])
        print(f"meshadmin service stopped for context {context_name}")


@service_app.command(name="logs")
def service_logs(
    follow: Annotated[
        bool,
        typer.Option("--follow", "-f", help="Follow the logs in real time"),
    ] = False,
    lines: Annotated[
        int,
        typer.Option("--lines", "-n", help="Number of lines to show"),
    ] = 50,
):
    context = get_context_config()
    context_name = context["name"]
    network_dir = context["network_dir"]
    os_name = platform.system()

    if os_name == "Darwin":
        error_log = network_dir / "error.log"
        output_log = network_dir / "output.log"

        if not error_log.exists() and not output_log.exists():
            print(
                f"No log files found for context {context_name}. Has the service been started?"
            )
            raise typer.Exit(1)

        if follow:
            try:
                process = subprocess.Popen(
                    ["tail", "-f", str(error_log), str(output_log)],
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
        else:
            for log_file in [output_log, error_log]:
                if log_file.exists():
                    print(f"\n=== {log_file.name} ===")
                    result = subprocess.run(
                        ["tail", f"-n{lines}", str(log_file)],
                        capture_output=True,
                        text=True,
                    )
                    print(result.stdout)
    else:
        try:
            cmd = ["journalctl", "-u", f"meshadmin-{context_name}"]
            if follow:
                cmd.append("-f")
            if lines:
                cmd.append(f"-n{lines}")

            if follow:
                process = subprocess.Popen(
                    cmd,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )
                process.wait()
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                print(result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"Error accessing logs: {e}")
            print(
                "Make sure the service is installed and you have appropriate permissions."
            )
            raise typer.Exit(1)
