import httpx
import pytest
from typer.testing import CliRunner

from meshadmin.cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_host_access_token(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.host.get_access_token", return_value="fake-token"
    )


@pytest.fixture
def mock_host_context_config(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.host.get_context_config",
        return_value={"endpoint": "http://testserver"},
    )


@pytest.fixture
def mock_download(mocker):
    return mocker.patch("meshadmin.cli.commands.host.download")


@pytest.fixture
def mock_host_get_config_from_mesh(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.host.get_config_from_mesh",
        return_value=(
            "pki: ca: test-ca-cert cert: test-host-cert key: host.key lighthouse: am_lighthouse: false hosts: - 10.0.0.1 static_host_map: '10.0.0.1': ['lighthouse.example.com:4242']",
            5,
            "false",
        ),
    )


@pytest.fixture
def test_context(temp_config_dir):
    result = runner.invoke(
        app,
        [
            "--config-path",
            str(temp_config_dir),
            "context",
            "create",
            "test-context-two",
            "--endpoint",
            "http://localhost:8001",
        ],
    )
    return result


@pytest.fixture
def mock_enroll_response(mocker):
    return mocker.patch(
        "httpx.post",
        return_value=httpx.Response(
            status_code=200,
            request=httpx.Request("POST", "http://testserver/api/v1/enroll"),
        ),
    )


def test_host_enrollment(
    mock_enroll_response,
    temp_config_dir,
    sample_context,
    mock_download,
    mock_host_get_config_from_mesh,
):
    result = runner.invoke(
        app,
        [
            "--config-path",
            str(temp_config_dir),
            "host",
            "enroll",
            "test-enrollment-key",
            "--preferred-hostname",
            "test-host",
            "--public-ip",
            "192.168.1.100",
        ],
    )
    assert result.exit_code == 0
    network_dir = temp_config_dir / "networks" / "test-context"
    auth_key_path = temp_config_dir / "auth.key"
    public_key_path = network_dir / "host.pub"
    private_key_path = network_dir / "host.key"
    config_path = network_dir / "config.yaml"
    assert network_dir.exists()
    assert auth_key_path.exists()
    assert public_key_path.exists()
    assert private_key_path.exists()
    assert config_path.exists()
    mock_download.assert_called()
    mock_host_get_config_from_mesh.assert_called()
    assert "enrollment finished" in result.stdout
    result = runner.invoke(
        app,
        [
            "--config-path",
            str(temp_config_dir),
            "host",
            "enroll",
            "test-enrollment-key",
        ],
    )
    assert result.exit_code == 0
    assert "private and public nebula key already exists" in result.stdout


def test_host_enrollment_shared_auth_key(
    mock_enroll_response,
    temp_config_dir,
    sample_context,
    test_context,
    mock_download,
    mock_host_get_config_from_mesh,
):
    result = runner.invoke(
        app,
        [
            "--config-path",
            str(temp_config_dir),
            "--context",
            "test-context",
            "host",
            "enroll",
            "test-key",
        ],
    )
    assert result.exit_code == 0
    assert "enrollment finished" in result.stdout
    auth_key_path = temp_config_dir / "auth.key"
    original_auth_key = auth_key_path.read_text()
    result = runner.invoke(
        app,
        [
            "--config-path",
            str(temp_config_dir),
            "--context",
            "test-context-two",
            "host",
            "enroll",
            "test-key",
        ],
    )
    assert result.exit_code == 0
    assert "enrollment finished" in result.stdout
    assert auth_key_path.read_text() == original_auth_key


def test_delete_host_success(mocker, mock_host_access_token, mock_host_context_config):
    mock_response = httpx.Response(
        status_code=200,
        json={"message": "Host test-host deleted"},
        request=httpx.Request("DELETE", "http://testserver/api/v1/hosts/test-host"),
    )
    mock_delete = mocker.patch("httpx.delete", return_value=mock_response)
    result = runner.invoke(app, ["host", "delete", "test-host"])
    assert result.exit_code == 0
    mock_delete.assert_called_once_with(
        "http://testserver/api/v1/hosts/test-host",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert "deleted" in result.stdout.lower()


def test_delete_host_auth_failure(mock_host_access_token, mock_host_context_config):
    mock_host_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(app, ["host", "delete", "test-host"])
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout
