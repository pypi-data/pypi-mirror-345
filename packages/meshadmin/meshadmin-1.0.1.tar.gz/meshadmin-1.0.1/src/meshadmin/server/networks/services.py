import copy
import hashlib
import ipaddress
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
import yaml
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT

from meshadmin.common.utils import create_ca, print_ca, sign_keys
from meshadmin.server import assets
from meshadmin.server.networks.models import (
    CA,
    Group,
    Host,
    HostCert,
    HostConfig,
    Network,
    NetworkMembership,
    Rule,
    SigningCA,
    Template,
)

User = get_user_model()
logger = structlog.get_logger(__name__)


def create_available_hosts_iterator(cidr, unavailable_ips):
    network = ipaddress.IPv4Network(cidr)
    hosts_iterator = (
        host for host in network.hosts() if str(host) not in unavailable_ips
    )
    return hosts_iterator


def network_available_hosts_iterator(network):
    reserved_ips = [
        host.assigned_ip for host in Host.objects.filter(network=network).all()
    ]
    ipv4_iterator = create_available_hosts_iterator(network.cidr, reserved_ips)
    return ipv4_iterator


def create_network_ca(ca_name, network):
    cert, key = create_ca(ca_name)
    cert_print = print_ca(cert)
    ca = CA.objects.create(
        network=network, name=ca_name, cert=cert, key=key, cert_print=cert_print
    )
    return ca


def create_network(
    network_name: str, network_cidr: str, user: User, update_interval: int = 5
):
    logger.info("creating network")
    network = Network.objects.create(
        name=network_name, cidr=network_cidr, update_interval=update_interval
    )
    NetworkMembership.objects.create(
        network=network, user=user, role=NetworkMembership.Role.ADMIN
    )

    ca_name = "auto created initial ca"
    cert, key = create_ca(ca_name)
    json_data = print_ca(cert)
    ca = CA.objects.create(
        network=network, name=ca_name, cert=cert, key=key, cert_print=json_data
    )

    SigningCA.objects.create(network=network, ca=ca)
    logger.info("created network", network=str(network))
    return network


def apply_group_config_overrides(config_data: dict, groups: list[Group]) -> dict:
    config = copy.deepcopy(config_data)
    overrides = []
    for group in groups:
        for override in group.config_overrides.all():
            overrides.append((group.name, override))

    # Sort overrides by group name to ensure consistent ordering
    overrides.sort(key=lambda x: x[0])

    for group_name, override in overrides:
        try:
            path_parts = override.key.split(".")
            current = config
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            value = override.value
            if any(
                override.key.endswith(suffix)
                for suffix in [
                    ".serve_dns",
                ]
            ):
                value = value.lower() == "true"
            elif any(
                override.key.endswith(suffix)
                for suffix in [
                    ".port",
                ]
            ):
                value = int(value)

            current[path_parts[-1]] = value
            logger.info(
                "applied group config override",
                group=group_name,
                path=override.key,
                value=value,
            )
        except Exception as e:
            logger.error(
                "failed to apply group config override",
                group=group_name,
                path=override.key,
                error=str(e),
            )

    return config


def generate_config_yaml(host_id: int, ignore_freeze: bool = False):
    host = Host.objects.get(id=host_id)
    if host.config_freeze and not ignore_freeze:
        last_config = host.hostconfig_set.order_by("-created_at").first()
        if last_config:
            logger.info("using frozen config", host_id=host.id, host_name=host.name)
            return last_config.config

    logger.info("generating config", host_id=host.id, host_name=host.name)

    network = host.network
    ca = network.signingca.ca

    assert host.public_key
    # load config yaml
    config_template = (assets.asset_path / "config.yml").read_text()
    config_data = yaml.safe_load(config_template)
    config_data["pki"]["ca"] = "".join([ca.cert for ca in network.ca_set.all()])

    groups = frozenset([group.name for group in host.groups.all()])
    assigned_ip = f"{host.assigned_ip}/24"

    group_timestamps = frozenset([group.updated_at for group in host.groups.all()])
    group_rules = frozenset(
        [rule.updated_at for group in host.groups.all() for rule in group.rules.all()]
    )
    group_configs = frozenset(
        [
            config.updated_at
            for group in host.groups.all()
            for config in group.config_overrides.all()
        ]
    )

    query_key = (
        ca.cert,
        host.public_key,
        host.name,
        assigned_ip,
        hash(group_timestamps),
        hash(group_rules),
        hash(group_configs),
    )
    query_key_hash = hash(query_key)
    host_cert = HostCert.objects.filter(host=host, ca=ca).first()
    if host_cert is None or host_cert.hash != query_key_hash:
        logger.info(
            "generating new host certificate",
            host_id=host.id,
            host_name=host.name,
            reason="initial" if host_cert is None else "hash_changed",
        )
        if host_cert:
            host_cert.delete()

        cert = sign_keys(
            ca_key=ca.key,
            ca_crt=ca.cert,
            public_key=host.public_key,
            name=host.name,
            ip=assigned_ip,
            groups=groups,
        )
        host_cert = HostCert.objects.create(
            host=host, ca=ca, cert=cert, hash=query_key_hash
        )

    config_data["pki"]["cert"] = host_cert.cert
    config_data["pki"]["key"] = "host.key"

    lighthouses = Host.objects.filter(network=network, is_lighthouse=True).all()
    if host.is_lighthouse:
        config_data["lighthouse"]["am_lighthouse"] = True
        config_data["lighthouse"]["hosts"] = []
    else:
        config_data["lighthouse"]["am_lighthouse"] = False
        config_data["lighthouse"]["hosts"] = [
            lighthouse.assigned_ip for lighthouse in lighthouses
        ]
    config_data["static_host_map"] = {
        lighthouse.assigned_ip: [f"{lighthouse.public_ip_or_hostname}:4242"]
        for lighthouse in lighthouses
    }
    config_data["relay"]["am_relay"] = host.is_relay
    config_data["relay"]["use_relays"] = host.use_relay

    config_data["tun"]["dev"] = host.interface

    inbound_rules = []
    outbound_rules = []
    for group in host.groups.all():
        for rule in group.rules.all():
            rule_data = {}

            if rule.local_cidr is not None:
                rule_data["local_cidr"] = rule.local_cidr

            if rule.cidr is not None:
                rule_data["cidr"] = rule.cidr

            groups = rule.groups.all()
            if len(groups) > 0:
                rule_data["groups"] = [group.name for group in groups]

            if rule.group is not None:
                rule_data["group"] = rule.group.name

            if rule.proto is not None:
                rule_data["proto"] = rule.proto

            if rule.port is not None:
                rule_data["port"] = rule.port

            if rule.direction == Rule.Direction.INBOUND:
                inbound_rules.append(rule_data)
            else:
                outbound_rules.append(rule_data)

    config_data["firewall"]["inbound"] = inbound_rules
    config_data["firewall"]["outbound"] = outbound_rules

    config_data = apply_group_config_overrides(config_data, host.groups.all())

    yaml_config = yaml.safe_dump(config_data, indent=4)

    sha256 = hashlib.sha256(yaml_config.encode()).hexdigest()

    if not HostConfig.objects.filter(sha256=sha256).exists():
        logger.info("saving new config version", host_id=host.id, host_name=host.name)
        HostConfig.objects.create(host=host, config=yaml_config, sha256=sha256)
    else:
        logger.debug("config unchanged", host_id=host.id, host_name=host.name)

    return yaml_config


def create_template(
    name: str,
    network_name: str,
    is_lighthouse=False,
    is_relay: bool = False,
    use_relay: bool = True,
    groups: list[str] = (),
    reusable: bool = True,
    usage_limit: int = None,
    ephemeral_peers: bool = False,
    expires_at: datetime = None,
):
    template = Template.objects.create(
        name=name,
        network=Network.objects.get(name=network_name),
        is_lighthouse=is_lighthouse,
        is_relay=is_relay,
        use_relay=use_relay,
        reusable=reusable,
        usage_limit=usage_limit,
        ephemeral_peers=ephemeral_peers,
        expires_at=expires_at,
    )

    for group in groups:
        try:
            template.groups.add(
                Group.objects.get(name=group, network__name=network_name)
            )
        except Group.DoesNotExist:
            raise LookupError(f"Group does not exist in network {group}/{network_name}")

    return template


def get_server_signing_key():
    key_path = Path("enrollment_signing.key")
    if os.path.exists(key_path):
        with open(key_path, "r") as f:
            return JWK.from_json(f.read())
    else:
        key = JWK.generate(kty="EC", crv="P-256")
        with open(key_path, "w") as f:
            f.write(key.export_private())
        os.chmod(key_path, 0o600)
        return key


def generate_enrollment_token(template: Template):
    signing_key = get_server_signing_key()
    claims = {
        "jti": str(template.enrollment_key),
        "iss": "meshadmin",
        "sub": f"template:{template.id}",
        "iat": int(now().timestamp()),
        "template_id": template.id,
        "network_id": template.network_id,
        "is_lighthouse": template.is_lighthouse,
        "is_relay": template.is_relay,
        "use_relay": template.use_relay,
        "reusable": template.reusable,
        "usage_limit": template.usage_limit,
        "ephemeral_peers": template.ephemeral_peers,
    }
    if template.expires_at:
        claims["exp"] = int(template.expires_at.timestamp())
    token = JWT(header={"alg": "ES256"}, claims=claims)
    token.make_signed_token(signing_key)
    return token.serialize()


def verify_enrollment_token(token_string):
    signing_key = get_server_signing_key()
    try:
        token = JWT(jwt=token_string)
        token.validate(signing_key)
        payload = json.loads(token.token.objects["payload"])
        template_id = payload.get("template_id")
        if not template_id:
            raise ValueError("Invalid token: missing template_id")
        return template_id
    except Exception as e:
        error_message = str(e)
        if "Expired" in error_message:
            raise ValueError("Enrollment token has expired")
        elif "Invalid signature" in error_message:
            raise ValueError("Invalid enrollment token signature")
        else:
            logger.error(
                "invalid enrollment token", token=token_string, error=error_message
            )
            raise ValueError(f"Invalid enrollment token: {error_message}")


def enrollment(
    enrollment_key: str,
    public_auth_key: str,
    enroll_on_existence: bool,
    public_ip: str,
    preferred_hostname,
    public_net_key,
    interface: str = "nebula1",
):
    try:
        template_id = verify_enrollment_token(enrollment_key)
        template = Template.objects.get(id=template_id)
    except ValueError as e:
        logger.error("invalid enrollment token", error=str(e))
        raise ValueError(f"Invalid enrollment token: {str(e)}")
    except Template.DoesNotExist:
        logger.error("template not found", template_id=template_id)
        raise ValueError("Template not found")

    # Check usage limit
    if not template.reusable:
        if template.usage_count >= 1:
            logger.error(
                "single-use enrollment key has already been used",
                template_id=template.id,
            )
            raise ValueError("Single-use enrollment key has already been used")
    elif template.usage_limit:
        if template.usage_count >= template.usage_limit:
            logger.error("enrollment key usage limit exceeded", template_id=template.id)
            raise ValueError("Enrollment key usage limit exceeded")

    # check if public key is already enrolled
    thumbprint = JWK.from_json(public_auth_key).thumbprint()
    host: Optional[Host] = Host.objects.filter(public_auth_kid=thumbprint).first()

    # host already registered
    if host:
        if enroll_on_existence:
            logger.info(
                "host already exists, aborting enrollment",
                host_id=host.id,
                enroll_on_existence=enroll_on_existence,
            )
            raise ValueError("Host already enrolled")

        else:
            host.delete()

    network = template.network
    ipv4_iterator = network_available_hosts_iterator(network)

    if template.is_lighthouse and not public_ip:
        raise ValueError("Cannot enroll a lighthouse without public_ip")

    jwk_public_auth = JWK.from_json(public_auth_key)

    already_registered_hostnames = (
        Host.objects.values("name")
        .filter(network=network, name__startswith=preferred_hostname)
        .all()
    )
    final_hostname = preferred_hostname
    i = 1
    existing_hostnames = set([host["name"] for host in already_registered_hostnames])
    while final_hostname in existing_hostnames:
        final_hostname = f"{preferred_hostname}-{i}"
        i += 1

    host = Host.objects.create(
        network=network,
        name=final_hostname,
        assigned_ip=next(ipv4_iterator),
        is_relay=template.is_relay,
        is_lighthouse=template.is_lighthouse,
        public_ip_or_hostname=public_ip,
        public_key=public_net_key,
        public_auth_key=public_auth_key,
        public_auth_kid=jwk_public_auth.thumbprint(),
        is_ephemeral=template.ephemeral_peers,
        interface=interface,
    )

    # Increment usage count
    template.usage_count += 1
    template.save()

    for group in template.groups.all():
        host.groups.add(group)

    host.save()
    return host


def create_group(network_pk: int, group_name: str, description: str = ""):
    network = Network.objects.get(pk=network_pk)
    return Group.objects.create(
        network=network, name=group_name, description=description
    )
