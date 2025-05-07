import httpx
import pytest
from typer.testing import CliRunner

from meshadmin.cli.main import app

runner = CliRunner()

MOCK_TEMPLATE_CREATE = {"id": 1, "name": "test-template", "enrollment_key": "abc123"}

MOCK_TEMPLATE_TOKEN = "1234567890"


@pytest.fixture
def mock_template_access_token(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.template.get_access_token", return_value="fake-token"
    )


@pytest.fixture
def mock_template_context_config(mocker):
    return mocker.patch(
        "meshadmin.cli.commands.template.get_context_config",
        return_value={"endpoint": "http://testserver"},
    )


def test_create_template_success(
    mocker, mock_template_access_token, mock_template_context_config
):
    mock_response = httpx.Response(
        status_code=200,
        json=MOCK_TEMPLATE_CREATE,
        request=httpx.Request("POST", "http://testserver/api/v1/templates"),
    )
    mock_post = mocker.patch("httpx.post", return_value=mock_response)
    result = runner.invoke(
        app,
        [
            "template",
            "create",
            "test-network",
            "test-template",
            "true",
            "false",
            "false",
        ],
    )
    assert result.exit_code == 0
    mock_post.assert_called_once()
    assert "test-template" in result.stdout
    assert "abc123" in result.stdout


def test_create_template_auth_failure(
    mock_template_access_token, mock_template_context_config
):
    mock_template_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(
        app,
        [
            "template",
            "create",
            "test-network",
            "test-template",
            "true",
            "false",
            "false",
        ],
    )
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout


def test_get_template_token_success(
    mocker, mock_template_access_token, mock_template_context_config
):
    mock_response = httpx.Response(
        status_code=200,
        text=MOCK_TEMPLATE_TOKEN,
        request=httpx.Request(
            "GET", "http://testserver/api/v1/templates/test-template/token"
        ),
    )
    mock_get = mocker.patch("httpx.get", return_value=mock_response)
    result = runner.invoke(app, ["template", "get-token", "test-template"])
    assert result.exit_code == 0
    mock_get.assert_called_once_with(
        "http://testserver/api/v1/templates/test-template/token",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert MOCK_TEMPLATE_TOKEN in result.stdout


def test_get_template_token_auth_failure(
    mock_template_access_token, mock_template_context_config
):
    mock_template_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(app, ["template", "get-token", "test-template"])
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout


def test_delete_template_success(
    mocker, mock_template_access_token, mock_template_context_config
):
    mock_response = httpx.Response(
        status_code=200,
        json={"message": "Template test-template deleted"},
        request=httpx.Request(
            "DELETE", "http://testserver/api/v1/templates/test-template"
        ),
    )
    mock_delete = mocker.patch("httpx.delete", return_value=mock_response)
    result = runner.invoke(app, ["template", "delete", "test-template"])
    assert result.exit_code == 0
    mock_delete.assert_called_once_with(
        "http://testserver/api/v1/templates/test-template",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert "deleted" in result.stdout.lower()


def test_delete_template_auth_failure(
    mock_template_access_token, mock_template_context_config
):
    mock_template_access_token.side_effect = Exception("Auth failed")
    result = runner.invoke(app, ["template", "delete", "test-template"])
    assert result.exit_code == 1
    assert "failed to get access token" in result.stdout
