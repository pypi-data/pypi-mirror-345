import pytest

from meshadmin.server.networks.services import create_network


@pytest.fixture
def create_test_password() -> str:
    return "123test"


@pytest.fixture
def create_user(django_user_model, create_test_password):
    def _make_user(
        username="testuser", email="test@example.com", password=create_test_password
    ):
        return django_user_model.objects.create_user(
            username=username, email=email, password=password
        )

    return _make_user


@pytest.fixture
def auth_client(client, create_user, create_test_password):
    def _make_auth_client(username="testuser"):
        user = create_user(username=username)
        client.login(username=user.username, password=create_test_password)
        return client, user

    return _make_auth_client


@pytest.fixture
def test_network(create_user):
    def _create_network(name="test_network", cidr="100.100.64.0/24", user=None):
        if user is None:
            user = create_user()
        return create_network(name, cidr, user=user)

    return _create_network
