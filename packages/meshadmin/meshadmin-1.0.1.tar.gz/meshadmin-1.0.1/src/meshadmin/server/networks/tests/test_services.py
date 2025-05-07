from datetime import timedelta

import pytest
import yaml
from django.db import IntegrityError
from django.utils import timezone
from jwcrypto.jwk import JWK

from meshadmin.common.utils import create_keys
from meshadmin.server.networks.models import GroupConfig, Host, Rule
from meshadmin.server.networks.services import (
    apply_group_config_overrides,
    create_available_hosts_iterator,
    create_group,
    create_network_ca,
    create_template,
    enrollment,
    generate_config_yaml,
    generate_enrollment_token,
    network_available_hosts_iterator,
)


def test_create_available_hosts_iterator():
    cidr = "192.168.1.0/24"
    iterator = create_available_hosts_iterator(cidr, [])
    first_ip = next(iterator)
    assert str(first_ip) == "192.168.1.1"


def test_create_available_hosts_iterator_with_unavailable_ips():
    cidr = "192.168.1.0/24"
    unavailable = ["192.168.1.1", "192.168.1.2"]
    iterator = create_available_hosts_iterator(cidr, unavailable)
    first_available = next(iterator)
    assert str(first_available) == "192.168.1.3"


def test_network_available_hosts_iterator(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    Host.objects.create(
        network=network,
        name="host1",
        assigned_ip="10.0.0.1",
        public_key="test",
    )
    Host.objects.create(
        network=network,
        name="host2",
        assigned_ip="10.0.0.2",
        public_key="test",
    )
    iterator = network_available_hosts_iterator(network)
    first_available = next(iterator)
    assert str(first_available) == "10.0.0.3"


def test_create_network(test_network):
    network_name = "testnet"
    network_cidr = "100.100.64.0/24"
    test_net = test_network(name=network_name, cidr=network_cidr)
    assert test_net.name == network_name
    assert test_net.cidr == network_cidr
    assert test_net.signingca.ca.name == "auto created initial ca"
    assert test_net.signingca.ca.cert is not None
    assert test_net.signingca.ca.key is not None
    assert test_net.signingca.ca.cert_print is not None
    assert (
        test_net.signingca.ca.cert_print["details"]["name"] == "auto created initial ca"
    )
    assert test_net.signingca.ca.cert_print["details"]["isCa"] is True


def test_cannot_create_duplicate_groups_for_the_same_network(test_network):
    test_net = test_network(name="testnet", cidr="100.100.64.0/24")
    create_group(test_net.pk, "group1")
    with pytest.raises(IntegrityError):
        create_group(test_net.pk, "group1")


def test_cannot_create_a_template_based_on_a_non_existing_group(test_network):
    test_net = test_network(name="testnet", cidr="100.100.64.0/24")
    with pytest.raises(LookupError):
        create_template(
            "hosts",
            test_net.name,
            is_lighthouse=False,
            is_relay=False,
            use_relay=True,
            groups=["group1", "group2"],
        )


def test_generate_config_yaml_with_firewall(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    create_network_ca("test_ca", network)
    _, public_key = create_keys()

    host = Host.objects.create(
        network=network,
        name="test_host",
        assigned_ip="10.0.0.1",
        public_key=public_key,
        interface="nebula1",
    )

    security_group = create_group(
        network.id, "test_security_group", "Test security group"
    )
    host.groups.add(security_group)
    host.save()

    group1 = create_group(network.id, "group1")
    group2 = create_group(network.id, "group2")
    rule = Rule.objects.create(
        security_group=security_group,
        direction=Rule.Direction.INBOUND,
        port="80",
        proto="tcp",
        cidr="0.0.0.0/0",
        local_cidr="10.0.0.0/24",
        group=group1,
    )
    rule.groups.add(group1, group2)

    # Outbound rules
    Rule.objects.create(
        security_group=security_group,
        direction=Rule.Direction.OUTBOUND,
        port="443",
        proto="tcp",
        cidr="0.0.0.0/0",
    )
    Rule.objects.create(
        security_group=security_group,
        direction=Rule.Direction.OUTBOUND,
        proto="udp",
    )

    config_yaml = generate_config_yaml(host.id)
    config_dict = yaml.safe_load(config_yaml)

    # Verify firewall configuration exists
    assert "firewall" in config_dict
    assert "inbound" in config_dict["firewall"]
    assert "outbound" in config_dict["firewall"]
    assert len(config_dict["firewall"]["inbound"]) == 1
    assert len(config_dict["firewall"]["outbound"]) == 2

    # Verify inbound rule with all attributes
    inbound_rule = config_dict["firewall"]["inbound"][0]
    assert inbound_rule["port"] == "80"
    assert inbound_rule["proto"] == "tcp"
    assert inbound_rule["cidr"] == "0.0.0.0/0"
    assert inbound_rule["local_cidr"] == "10.0.0.0/24"
    assert inbound_rule["group"] == "group1"
    assert set(inbound_rule["groups"]) == {"group1", "group2"}

    # Verify simple outbound rule
    outbound_rule = config_dict["firewall"]["outbound"][0]
    assert outbound_rule["port"] == "443"
    assert outbound_rule["proto"] == "tcp"
    assert outbound_rule["cidr"] == "0.0.0.0/0"

    # Verify minimal outbound rule
    minimal_rule = config_dict["firewall"]["outbound"][1]
    assert minimal_rule["proto"] == "udp"
    assert minimal_rule["port"] == "any"
    assert "cidr" not in minimal_rule
    assert "local_cidr" not in minimal_rule
    assert "group" not in minimal_rule
    assert "groups" not in minimal_rule


def test_lighthouse_relay_configuration(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    create_network_ca("test_ca", network)

    lighthouse = Host.objects.create(
        network=network,
        name="lighthouse",
        assigned_ip="10.0.0.1",
        public_key=create_keys()[1],
        is_lighthouse=True,
        is_relay=True,
        public_ip_or_hostname="public.lighthouse.com",
    )
    host = Host.objects.create(
        network=network,
        name="client",
        assigned_ip="10.0.0.2",
        public_key=create_keys()[1],
        use_relay=True,
    )

    lighthouse_config = yaml.safe_load(generate_config_yaml(lighthouse.id))
    assert lighthouse_config["lighthouse"]["am_lighthouse"] is True
    assert lighthouse_config["relay"]["am_relay"] is True

    client_config = yaml.safe_load(generate_config_yaml(host.id))
    assert client_config["lighthouse"]["am_lighthouse"] is False
    assert client_config["lighthouse"]["hosts"] == ["10.0.0.1"]
    assert client_config["static_host_map"]["10.0.0.1"] == [
        "public.lighthouse.com:4242"
    ]
    assert client_config["relay"]["use_relays"] is True


def test_enrollment_with_existing_host_cases(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template("test_template", network.name)
    token = generate_enrollment_token(template)

    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    # Initial host
    host1 = enrollment(
        enrollment_key=token,
        public_net_key=public_key,
        public_auth_key=public_auth_key,
        preferred_hostname="test_host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )
    host1_id = host1.id

    # Case 1: enroll_on_existence=True should raise ValueError
    with pytest.raises(ValueError, match="Host already enrolled"):
        enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=public_auth_key,
            preferred_hostname="test_host2",
            public_ip="127.0.0.2",
            enroll_on_existence=True,
        )

    # Case 2: enroll_on_existence=False should delete old host and create new one
    host2 = enrollment(
        enrollment_key=token,
        public_net_key=public_key,
        public_auth_key=public_auth_key,
        preferred_hostname="test_host2",
        public_ip="127.0.0.2",
        enroll_on_existence=False,
    )
    assert host2.id != host1_id
    assert host2.name == "test_host2"
    assert host2.public_ip_or_hostname == "127.0.0.2"
    assert not Host.objects.filter(id=host1_id).exists()


def test_enrollment_lighthouse_without_public_ip(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "test_template", network.name, is_lighthouse=True, is_relay=False
    )
    token = generate_enrollment_token(template)

    with pytest.raises(
        ValueError, match="Cannot enroll a lighthouse without public_ip"
    ):
        enrollment(
            enrollment_key=token,
            public_net_key="test_key",
            public_auth_key=JWK.generate(kty="RSA").export_public(),
            preferred_hostname="test_host",
            public_ip=None,
            enroll_on_existence=False,
        )


def test_enrollment_hostname_increment(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template("test_template", network.name)
    token = generate_enrollment_token(template)

    for i in range(3):
        auth_key = JWK.generate(kty="RSA")
        _, public_key = create_keys()

        host = enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=auth_key.export_public(),
            preferred_hostname="test-host",
            public_ip=f"127.0.0.{i + 1}",
            enroll_on_existence=False,
        )

        if i == 0:
            assert host.name == "test-host"
        else:
            assert host.name == f"test-host-{i}"


def test_template_with_security_group(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    create_network_ca("test_ca", network)
    security_group = create_group(
        network.id, "test_security_group", "Test security group"
    )
    group1 = create_group(network.id, "group1")
    Rule.objects.create(
        security_group=security_group,
        direction=Rule.Direction.INBOUND,
        port="80",
        proto="tcp",
        group=group1,
    )
    template = create_template(
        "test_template",
        network.name,
        is_lighthouse=False,
        is_relay=False,
        use_relay=True,
        groups=[security_group.name],
    )
    token = generate_enrollment_token(template)
    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    host = enrollment(
        enrollment_key=token,
        public_net_key=public_key,
        public_auth_key=public_auth_key,
        preferred_hostname="test-host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )

    assert host.groups.count() == 1
    assert host.groups.first() == security_group


def test_non_reusable_enrollment_key(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "single_use_template",
        network.name,
        reusable=False,
    )
    token = generate_enrollment_token(template)

    # First enrollment should succeed
    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    host = enrollment(
        enrollment_key=token,
        public_net_key=public_key,
        public_auth_key=public_auth_key,
        preferred_hostname="test-host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )

    assert host is not None
    assert host.name == "test-host"

    # Second enrollment with same key should fail
    auth_key2 = JWK.generate(kty="RSA")
    public_auth_key2 = auth_key2.export_public()
    _, public_key2 = create_keys()

    with pytest.raises(
        ValueError, match="Single-use enrollment key has already been used"
    ):
        enrollment(
            enrollment_key=token,
            public_net_key=public_key2,
            public_auth_key=public_auth_key2,
            preferred_hostname="another-host",
            public_ip="127.0.0.2",
            enroll_on_existence=False,
        )


def test_enrollment_key_with_usage_limit(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "limited_use_template",
        network.name,
        reusable=True,
        usage_limit=2,
    )
    token = generate_enrollment_token(template)
    # First two enrollments should succeed
    for i in range(2):
        auth_key = JWK.generate(kty="RSA")
        public_auth_key = auth_key.export_public()
        _, public_key = create_keys()

        host = enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=public_auth_key,
            preferred_hostname=f"test-host-{i}",
            public_ip=f"127.0.0.{i + 1}",
            enroll_on_existence=False,
        )

        assert host is not None
        assert host.name == f"test-host-{i}"

    # Third enrollment should fail
    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    with pytest.raises(ValueError, match="Enrollment key usage limit exceeded"):
        enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=public_auth_key,
            preferred_hostname="test-host-3",
            public_ip="127.0.0.3",
            enroll_on_existence=False,
        )


def test_expired_enrollment_key(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "expired_template",
        network.name,
        expires_at=timezone.now() - timedelta(days=1),
    )
    token = generate_enrollment_token(template)

    # Enrollment should fail
    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    with pytest.raises(ValueError, match="Enrollment token has expired"):
        enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=public_auth_key,
            preferred_hostname="test-host",
            public_ip="127.0.0.1",
            enroll_on_existence=False,
        )


def test_ephemeral_peers_flag(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template(
        "ephemeral_template",
        network.name,
        ephemeral_peers=True,
    )
    token = generate_enrollment_token(template)

    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()

    host = enrollment(
        enrollment_key=token,
        public_net_key=public_key,
        public_auth_key=public_auth_key,
        preferred_hostname="test-host",
        public_ip="127.0.0.1",
        enroll_on_existence=False,
    )

    assert host is not None
    assert host.is_ephemeral is True

    # Test with ephemeral_peers=False
    template2 = create_template(
        "non_ephemeral_template",
        network.name,
        ephemeral_peers=False,
    )
    token2 = generate_enrollment_token(template2)
    auth_key2 = JWK.generate(kty="RSA")
    public_auth_key2 = auth_key2.export_public()
    _, public_key2 = create_keys()

    host2 = enrollment(
        enrollment_key=token2,
        public_net_key=public_key2,
        public_auth_key=public_auth_key2,
        preferred_hostname="test-host-2",
        public_ip="127.0.0.2",
        enroll_on_existence=False,
    )

    assert host2 is not None
    assert host2.is_ephemeral is False


def test_token_with_nonexistent_template(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    template = create_template("test_template", network.name)
    token = generate_enrollment_token(template)
    template.delete()
    auth_key = JWK.generate(kty="RSA")
    public_auth_key = auth_key.export_public()
    _, public_key = create_keys()
    with pytest.raises(ValueError, match="Template not found"):
        enrollment(
            enrollment_key=token,
            public_net_key=public_key,
            public_auth_key=public_auth_key,
            preferred_hostname="test-host",
            public_ip="127.0.0.1",
            enroll_on_existence=False,
        )


def test_apply_group_config_overrides(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    group1 = create_group(network.id, "group1")
    group2 = create_group(network.id, "group2")
    GroupConfig.objects.create(
        group=group1,
        key="lighthouse.serve_dns",
        value="true",
    )
    GroupConfig.objects.create(
        group=group1,
        key="lighthouse.dns.port",
        value="53",
    )
    GroupConfig.objects.create(
        group=group2,
        key="lighthouse.dns.host",
        value="8.8.8.8",
    )
    initial_config = {
        "firewall": {"outbound": [{}]},
    }
    updated_config = apply_group_config_overrides(initial_config, [group1, group2])
    assert updated_config["lighthouse"]["serve_dns"] is True
    assert updated_config["lighthouse"]["dns"]["port"] == 53
    assert updated_config["lighthouse"]["dns"]["host"] == "8.8.8.8"


def test_generate_config_yaml_with_config_overrides(test_network):
    network = test_network(name="testnet", cidr="10.0.0.0/24")
    create_network_ca("test_ca", network)
    group = create_group(network.id, "testgroup")
    _, public_key = create_keys()
    host = Host.objects.create(
        network=network,
        name="test_host",
        assigned_ip="10.0.0.1",
        public_key=public_key,
        interface="nebula1",
    )
    host.groups.add(group)
    GroupConfig.objects.create(
        group=group,
        key="lighthouse.serve_dns",
        value="true",
    )
    GroupConfig.objects.create(
        group=group,
        key="lighthouse.dns.port",
        value="53",
    )
    config = generate_config_yaml(host.id)
    config_dict = yaml.safe_load(config)
    assert config_dict["lighthouse"]["serve_dns"] is True
    assert config_dict["lighthouse"]["dns"]["port"] == 53
