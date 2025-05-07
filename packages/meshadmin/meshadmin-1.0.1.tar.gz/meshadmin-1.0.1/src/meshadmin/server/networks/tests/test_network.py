from uuid import uuid4

import pytest
import yaml
from jwcrypto.jwk import JWK
from syrupy.filters import paths

from meshadmin.common.utils import create_keys, get_nebula_cert_binary_path, print_ca
from meshadmin.server.networks.models import Rule
from meshadmin.server.networks.services import (
    create_group,
    create_template,
    enrollment,
    generate_config_yaml,
    generate_enrollment_token,
)


@pytest.fixture()
def full_network(test_network):
    test_net = test_network(name="testnet", cidr="100.100.64.0/24")

    lighthouse_template = create_template(
        "lighthouses", test_net.name, is_lighthouse=True, is_relay=True, use_relay=False
    )
    token = generate_enrollment_token(lighthouse_template)

    # enroll a lighthouses
    for i in range(1, 5):
        kid = str(uuid4())
        auth_key = JWK.generate(kty="RSA", kid=kid, size=2048)
        public_auth_key = auth_key.export_public()
        private_net_key, public_net_key = create_keys()

        preferred_hostname = str(uuid4())
        public_ip = f"127.0.0.{i}"

        enrollment(
            enrollment_key=token,
            public_net_key=public_net_key,
            public_auth_key=public_auth_key,
            preferred_hostname=preferred_hostname,
            public_ip=public_ip,
            enroll_on_existence=False,
        )

    for i in range(1, 7):
        create_group(test_net.pk, f"group {i}")

    return test_net


def test_nebula_bin_selection():
    nebula_cert_path = get_nebula_cert_binary_path()
    assert nebula_cert_path.exists()


def test_lighthouse_template(test_network, snapshot):
    test_net = test_network(name="testnet", cidr="100.100.64.0/24")
    lighthouse_template = create_template(
        "lighthouses", test_net.name, is_lighthouse=True, is_relay=True, use_relay=False
    )
    token = generate_enrollment_token(lighthouse_template)

    assert lighthouse_template.enrollment_key is not None

    # enroll a lighthouse
    kid = str(uuid4())
    auth_key = JWK.generate(kty="RSA", kid=kid, size=2048)
    public_auth_key = auth_key.export_public()
    private_net_key, public_net_key = create_keys()
    preferred_hostname = str(uuid4())
    public_ip = "127.0.0.1"

    host = enrollment(
        enrollment_key=token,
        public_net_key=public_net_key,
        public_auth_key=public_auth_key,
        preferred_hostname=preferred_hostname,
        public_ip=public_ip,
        enroll_on_existence=False,
    )

    assert host.network == test_net
    assert host.public_key == public_net_key
    assert host.public_auth_kid == auth_key.thumbprint()
    assert host.groups.count() == 0

    config_yaml = generate_config_yaml(host.id)
    config_dict = yaml.safe_load(config_yaml)

    assert config_dict == snapshot(exclude=paths("pki.ca", "pki.cert"))


def test_host_template(db, full_network, snapshot):
    group1 = create_group(full_network.pk, "group1")
    group2 = create_group(full_network.pk, "group2")
    security_group = create_group(
        full_network.pk, "test_security_group", "Test security group"
    )
    Rule.objects.create(
        security_group=security_group,
        direction=Rule.Direction.INBOUND,
        port="80",
        proto="tcp",
        group=group1,
    )

    host_template = create_template(
        "hosts",
        full_network.name,
        is_lighthouse=False,
        is_relay=False,
        use_relay=True,
        groups=[group1.name, group2.name, security_group.name],
    )
    token = generate_enrollment_token(host_template)

    # enroll the client host
    kid = str(uuid4())
    auth_key = JWK.generate(kty="RSA", kid=kid, size=2048)
    public_auth_key = auth_key.export_public()
    private_net_key, public_net_key = create_keys()
    preferred_hostname = str(uuid4())
    public_ip = "127.0.0.1"

    host1 = enrollment(
        enrollment_key=token,
        public_net_key=public_net_key,
        public_auth_key=public_auth_key,
        preferred_hostname=preferred_hostname,
        public_ip=public_ip,
        enroll_on_existence=False,
    )

    assert host1.hostcert_set.first() is None

    config_yaml = generate_config_yaml(host1.id)

    config_dict = yaml.safe_load(config_yaml)
    host_cert = config_dict["pki"]["cert"]
    assert host_cert

    host_cert_json = print_ca(host_cert)
    print(host_cert_json)
    assert sorted(host_cert_json["details"]["groups"]) == sorted(
        ["group1", "group2", "test_security_group"]
    )
    assert host_cert_json["details"]["name"] == str(host1.name)

    assert "firewall" in config_dict
    assert len(config_dict["firewall"]["inbound"]) == 1
    assert config_dict["firewall"]["inbound"][0]["port"] == "80"

    assert config_dict == snapshot(exclude=paths("pki.ca", "pki.cert"))
