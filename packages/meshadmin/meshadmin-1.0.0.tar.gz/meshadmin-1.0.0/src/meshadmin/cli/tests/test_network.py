import httpx
import pytest
from typer.testing import CliRunner

from meshadmin.cli.main import app

runner = CliRunner()

MOCK_NETWORK_LIST = [
    {"id": 1, "name": "test-network", "cidr": "10.0.0.0/24"},
    {"id": 2, "name": "prod-network", "cidr": "10.1.0.0/24"},
]

MOCK_NETWORK_CREATE = {"id": 1, "name": "new-network", "cidr": "10.2.0.0/24"}


@pytest.fixture
def mock_access_token(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.network.get_access_token", return_value="fake-token"
    )


@pytest.fixture
def mock_context_config(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.network.get_context_config",
        return_value={"endpoint": "http://testserver"},
    )


def test_list_networks_success(mocker, mock_access_token, mock_context_config):
    mock_response = httpx.Response(
        status_code=200,
        json=MOCK_NETWORK_LIST,
        request=httpx.Request("GET", "http://testserver/api/v1/networks"),
    )
    mock_get = mocker.patch("httpx.get", return_value=mock_response)
    result = runner.invoke(app, ["network", "list"])
    assert result.exit_code == 0
    mock_get.assert_called_once_with(
        "http://testserver/api/v1/networks",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert "test-network" in result.stdout
    assert "prod-network" in result.stdout


def test_list_networks_auth_failure(mock_access_token, mock_context_config):
    mock_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(app, ["network", "list"])
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout


def test_create_network_success(mocker, mock_access_token, mock_context_config):
    mock_response = httpx.Response(
        status_code=200,
        json=MOCK_NETWORK_CREATE,
        request=httpx.Request("POST", "http://testserver/api/v1/networks"),
    )
    mock_post = mocker.patch("httpx.post", return_value=mock_response)
    result = runner.invoke(app, ["network", "create", "new-network", "10.2.0.0/24"])
    assert result.exit_code == 0
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "http://testserver/api/v1/networks"
    assert call_args[1]["headers"] == {"Authorization": "Bearer fake-token"}
    assert "new-network" in result.stdout


def test_create_network_server_error(mocker, mock_access_token, mock_context_config):
    mock_response = httpx.Response(
        status_code=400,
        request=httpx.Request("POST", "http://testserver/api/v1/networks"),
    )
    mocker.patch("httpx.post", return_value=mock_response)
    result = runner.invoke(app, ["network", "create", "new-network", "invalid-cidr"])
    assert result.exit_code == 1
    assert "could not create network" in result.stdout


def test_create_network_auth_failure(mock_access_token, mock_context_config):
    mock_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(app, ["network", "create", "new-network", "10.2.0.0/24"])
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout
