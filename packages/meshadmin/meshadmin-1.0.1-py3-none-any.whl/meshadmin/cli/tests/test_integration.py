import json
import os
import subprocess
import time
from pathlib import Path

import pytest
import requests
from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def docker_compose_runtime():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    compose_file = root_dir / "docker-compose.test.yml"
    subprocess.run(
        ["docker", "compose", "-f", str(compose_file), "up", "--build", "-d"],
        check=True,
    )

    # Wait for server to be ready
    max_retries = 5
    retry_interval = 1
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/api/v1/test")
            if response.status_code == 200:
                print(f"Server ready after {attempt + 1} attempts")
                break
        except ConnectionError:
            if attempt + 1 < max_retries:
                print(f"Waiting for server (attempt {attempt + 1}/{max_retries})...")
                time.sleep(retry_interval)
            else:
                subprocess.run(
                    ["docker", "compose", "-f", str(compose_file), "logs"],
                    check=True,
                )
                raise Exception("Server failed to become ready")

    yield

    # Cleanup
    subprocess.run(
        ["docker", "compose", "-f", str(compose_file), "down", "-v"], check=True
    )


@pytest.mark.runtime
def test_complete_workflow(docker_compose_runtime, temp_config_dir):
    # 1. Create a context
    result = subprocess.run(
        [
            "meshadmin",
            "--config-path",
            str(temp_config_dir),
            "context",
            "create",
            "integration-test",
            "--endpoint",
            "http://localhost:8000",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Set 'integration-test' as active context" in result.stdout
    context_dir = temp_config_dir / "contexts.yaml"
    assert context_dir.exists(), "Context file not created"

    test_env = {
        "MESHADMIN_TEST_MODE": "true",
        "MESHADMIN_CONFIG_PATH": str(temp_config_dir),
        "MESH_CONTEXT": "integration-test",
        **os.environ,
    }

    # 2. Create a network
    result = subprocess.run(
        [
            "meshadmin",
            "network",
            "create",
            "test-network",
            "100.100.100.0/24",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=test_env,
    )
    assert "test-network" in result.stdout

    # 3. Create a template
    result = subprocess.run(
        [
            "meshadmin",
            "template",
            "create",
            "test-template",
            "test-network",
            "true",
            "false",
            "false",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=test_env,
    )
    assert "test-template" in result.stdout

    # 4. Get the template token
    result = subprocess.run(
        [
            "meshadmin",
            "template",
            "get-token",
            "test-template",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=test_env,
    )
    token = json.loads(result.stdout.strip())["token"]

    # 5. Enroll a host
    result = subprocess.run(
        [
            "meshadmin",
            "host",
            "enroll",
            token,
        ],
        check=True,
        capture_output=True,
        text=True,
        env=test_env,
    )
    assert "enrollment finished" in result.stdout
    network_dir = temp_config_dir / "networks" / "integration-test"
    assert network_dir.exists(), "Network directory not created"
    private_key_path = network_dir / "host.key"
    public_key_path = network_dir / "host.pub"
    assert private_key_path.exists(), "Private key not created"
    assert public_key_path.exists(), "Public key not created"
    config_path = network_dir / "config.yaml"
    assert config_path.exists(), "Config file not created"
