from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from meshadmin.common.utils import create_keys
from meshadmin.server.networks.models import (
    CA,
    ConfigRollout,
    Group,
    GroupConfig,
    Host,
    HostConfig,
    Network,
    Rule,
    Template,
)
from meshadmin.server.networks.services import create_group, create_template


class TestRolloutViews:
    def test_rollout_creation_with_hosts(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        hosts = []
        for i in range(3):
            host = Host.objects.create(
                network=test_net,
                name=f"test-host-{i}",
                assigned_ip=f"100.100.64.{i + 1}",
            )
            hosts.append(host)

        data = {
            "name": "new-rollout",
            "notes": "Test notes",
            "hosts": [host.id for host in hosts[:2]],
        }

        response = client.post(
            reverse(
                "networks:network-rollout-create", kwargs={"network_id": test_net.id}
            ),
            data,
        )

        assert response.status_code == 302
        rollout = ConfigRollout.objects.get(name="new-rollout")
        assert rollout.network == test_net
        assert rollout.notes == "Test notes"
        assert rollout.status == "PENDING"
        assert list(rollout.target_hosts.all()) == hosts[:2]
        for host in hosts[:2]:
            host.refresh_from_db()
            assert host.config_freeze is True

    def test_rollout_unfreeze(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        hosts = []
        for i in range(2):
            host = Host.objects.create(
                network=test_net,
                name=f"test-host-{i}",
                assigned_ip=f"100.100.64.{i + 1}",
                config_freeze=True,
            )
            hosts.append(host)

        rollout = ConfigRollout.objects.create(
            name="test-rollout",
            network=test_net,
            status="PENDING",
        )
        rollout.target_hosts.add(*hosts)

        # Test single host unfreeze
        response = client.post(
            reverse("networks:rollout-unfreeze", kwargs={"pk": rollout.pk}),
            {"host_id": hosts[0].id},
        )

        assert response.status_code == 302
        rollout.refresh_from_db()
        assert rollout.status == "PENDING"
        assert list(rollout.completed_hosts.all()) == [hosts[0]]
        hosts[0].refresh_from_db()
        assert hosts[0].config_freeze is False
        hosts[1].refresh_from_db()
        assert hosts[1].config_freeze is True

        # Test complete rollout unfreeze
        response = client.post(
            reverse("networks:rollout-unfreeze", kwargs={"pk": rollout.pk}),
        )
        assert response.status_code == 302
        rollout.refresh_from_db()
        assert rollout.status == "COMPLETED"
        assert set(rollout.completed_hosts.all()) == set(hosts)
        for host in hosts:
            host.refresh_from_db()
            assert host.config_freeze is False

    def test_rollout_update(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        hosts = []
        for i in range(3):
            host = Host.objects.create(
                network=test_net,
                name=f"test-host-{i}",
                assigned_ip=f"100.100.64.{i + 1}",
            )
            hosts.append(host)

        rollout = ConfigRollout.objects.create(
            name="test-rollout",
            network=test_net,
            status="PENDING",
        )
        rollout.target_hosts.add(*hosts[:2])

        data = {
            "name": "updated-rollout",
            "notes": "Updated notes",
            "hosts": [hosts[0].id, hosts[2].id],
        }

        response = client.post(
            reverse("networks:rollout-edit", kwargs={"pk": rollout.pk}),
            data,
        )

        assert response.status_code == 302
        rollout.refresh_from_db()
        assert rollout.name == "updated-rollout"
        assert rollout.notes == "Updated notes"
        assert list(rollout.target_hosts.all()) == [hosts[0], hosts[2]]
        hosts[0].refresh_from_db()
        hosts[1].refresh_from_db()
        hosts[2].refresh_from_db()
        assert hosts[0].config_freeze is True
        assert hosts[1].config_freeze is False
        assert hosts[2].config_freeze is True

    def test_rollout_delete(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        hosts = []
        for i in range(2):
            host = Host.objects.create(
                network=test_net,
                name=f"test-host-{i}",
                assigned_ip=f"100.100.64.{i + 1}",
                config_freeze=True,
            )
            hosts.append(host)

        rollout = ConfigRollout.objects.create(
            name="test-rollout",
            network=test_net,
            status="PENDING",
        )
        rollout.target_hosts.add(*hosts)

        response = client.post(
            reverse("networks:rollout-delete", kwargs={"pk": rollout.pk}),
        )

        assert response.status_code == 302
        assert not ConfigRollout.objects.filter(pk=rollout.pk).exists()
        for host in hosts:
            host.refresh_from_db()
            assert host.config_freeze is False


class TestHostViews:
    def test_host_refresh_config_with_rollout(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        _, public_key = create_keys()
        host = Host.objects.create(
            network=test_net,
            name="test-host",
            assigned_ip="100.100.64.1",
            config_freeze=True,
            public_key=public_key,
            interface="nebula1",
        )
        rollout = ConfigRollout.objects.create(
            name="test-rollout",
            network=test_net,
            status="PENDING",
        )
        rollout.target_hosts.add(host)
        response = client.post(
            reverse(
                "networks:host-refresh-config",
                kwargs={"pk": host.pk, "rollout_id": rollout.pk},
            ),
        )
        assert response.status_code == 302
        assert response.url == reverse(
            "networks:rollout-detail", kwargs={"pk": rollout.pk}
        )
        host.refresh_from_db()
        assert host.hostconfig_set.count() > 0
        latest_config = host.hostconfig_set.latest("created_at")
        assert "pki" in latest_config.config
        assert "lighthouse" in latest_config.config

    def test_config_diff_view(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        host = Host.objects.create(name="test_host", network=test_net)

        # Create two configs with different content
        config1 = HostConfig.objects.create(
            host=host, config="test: config1\nline: 1", sha256="abc123"
        )
        config2 = HostConfig.objects.create(
            host=host, config="test: config2\nline: 2", sha256="def456"
        )

        # Test successful diff
        response = client.get(
            reverse(
                "networks:config-diff",
                kwargs={"base_id": config1.id, "compare_id": config2.id},
            )
        )
        assert response.status_code == 200
        assert b"-test: config1" in response.content
        assert b"+test: config2" in response.content
        assert b"-line: 1" in response.content
        assert b"+line: 2" in response.content

        # Test no changes between identical configs
        config3 = HostConfig.objects.create(
            host=host, config="test: config1\nline: 1", sha256="abc123"
        )
        response = client.get(
            reverse(
                "networks:config-diff",
                kwargs={"base_id": config1.id, "compare_id": config3.id},
            )
        )
        assert response.status_code == 200
        assert b"No differences found" in response.content

        # Test non-existent config
        response = client.get(
            reverse(
                "networks:config-diff",
                kwargs={"base_id": 99999, "compare_id": config2.id},
            )
        )
        assert response.status_code == 200
        assert b"Error" in response.content

    def test_make_signing_ca(self, auth_client, test_network):
        client, user = auth_client()
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        new_ca = CA.objects.create(
            network=network,
            name="new_signing_ca",
            key="test_key",
            cert="test_cert",
        )
        original_signing_ca = network.signingca.ca
        response = client.post(
            reverse("networks:ca-make-signing", kwargs={"pk": new_ca.pk}),
        )
        assert response.status_code == 200
        network.refresh_from_db()
        assert network.signingca.ca == new_ca
        assert network.signingca.ca != original_signing_ca


class TestCRUDWithParentNetwork:
    @pytest.mark.parametrize(
        "url_name,data,expected_model,expected_fields",
        [
            (
                "networks:network-ca-create",
                {"name": "test_ca"},
                CA,
                {"name": "test_ca", "cert__isnull": False, "key__isnull": False},
            ),
            (
                "networks:network-group-create",
                {"name": "test_group"},
                Group,
                {"name": "test_group"},
            ),
        ],
    )
    def test_entity_creation_with_parent_network(
        self,
        auth_client,
        test_network,
        url_name,
        data,
        expected_model,
        expected_fields,
    ):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        data["network"] = test_net.id

        response = client.post(
            reverse(url_name, kwargs={"network_id": test_net.id}),
            data,
        )
        assert response.status_code == 302
        filters = {**expected_fields, "network": test_net}
        assert expected_model.objects.filter(**filters).exists()

    @pytest.mark.parametrize(
        "url_name,model,update_data",
        [
            ("networks:ca-edit", CA, {"name": "updated_name"}),
            ("networks:group-edit", Group, {"name": "updated_name"}),
        ],
    )
    def test_entity_update_with_parent_network(
        self, auth_client, test_network, url_name, model, update_data
    ):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)

        obj = model.objects.create(
            network=test_net, name=f"test_{model._meta.model_name}"
        )
        update_data["network"] = test_net.id

        response = client.post(
            reverse(url_name, kwargs={"pk": obj.id}),
            update_data,
        )
        assert response.status_code == 302
        obj.refresh_from_db()
        assert obj.name == update_data["name"]

    @pytest.mark.parametrize(
        "url_name,model",
        [
            ("networks:ca-delete", CA),
            ("networks:group-delete", Group),
        ],
    )
    def test_entity_deletion_with_parent_network(
        self, auth_client, test_network, url_name, model
    ):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        obj = model.objects.create(
            network=test_net,
            name=f"test_{model._meta.model_name}",
        )
        response = client.post(
            reverse(url_name, kwargs={"pk": obj.id}),
        )
        assert response.status_code == 302
        assert not model.objects.filter(id=obj.id).exists()


class TestRuleViews:
    def test_add_rule_to_group_success(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)

        # First create a security group
        group_data = {"name": "test_group", "description": "Test security group"}
        response = client.post(
            reverse(
                "networks:network-group-create", kwargs={"network_id": test_net.id}
            ),
            group_data,
        )
        assert response.status_code == 302
        security_group = Group.objects.get(name="test_group")

        # create target groups
        target_group1 = create_group(test_net.pk, "target_group1")
        target_group2 = create_group(test_net.pk, "target_group2")
        target_group3 = create_group(test_net.pk, "target_group3")

        # add a rule to the group
        rule_data = {
            "security_group": security_group.id,
            "direction": "I",
            "proto": "tcp",
            "port": "80",
            "cidr": "0.0.0.0/0",
            "group": target_group1.id,
            "groups": [target_group2.id, target_group3.id],
            "local_cidr": "192.168.1.0/24",
        }

        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )

        assert response.status_code == 200
        assert Rule.objects.filter(security_group=security_group).exists()
        rule = Rule.objects.get(security_group=security_group)
        assert rule.direction == "I"
        assert rule.proto == "tcp"
        assert rule.port == "80"
        assert rule.cidr == "0.0.0.0/0"
        assert rule.group == target_group1
        assert set(rule.groups.all()) == {target_group2, target_group3}
        assert rule.local_cidr == "192.168.1.0/24"

    def test_add_rule_validation_no_target(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        rule_data = {
            "security_group": group.id,
            "direction": "I",
            "proto": "tcp",
            "port": "80",
        }
        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )
        assert response.status_code == 200
        assert "At least one of group, groups, or CIDR" in response.content.decode()
        assert not Rule.objects.filter(security_group=group).exists()

    def test_add_rule_validation_invalid_port(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        rule_data = {
            "security_group": group.id,
            "direction": "I",
            "proto": "tcp",
            "port": "80-invalid",
            "cidr": "0.0.0.0/0",
        }

        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )

        assert response.status_code == 200
        assert "Port range must be two" in response.content.decode()
        assert not Rule.objects.filter(security_group=group).exists()

        # Port out of range
        rule_data["port"] = "70000"
        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )
        assert response.status_code == 200
        assert "Port must be" in response.content.decode()
        assert not Rule.objects.filter(security_group=group).exists()

    def test_add_rule_validation_invalid_cidr(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        rule_data = {
            "security_group": group.id,
            "direction": "I",
            "proto": "tcp",
            "port": "80",
            "cidr": "invalid-cidr",
        }
        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )
        assert response.status_code == 200
        assert "Invalid CIDR format" in response.content.decode()
        assert not Rule.objects.filter(security_group=group).exists()

        # Invalid local CIDR format
        rule_data = {
            "security_group": group.id,
            "direction": "I",
            "proto": "tcp",
            "port": "80",
            "cidr": "0.0.0.0/0",
            "local_cidr": "invalid-local-cidr",
        }
        response = client.post(
            reverse("networks:group-add-rule"),
            rule_data,
        )
        assert response.status_code == 200
        assert "Invalid CIDR format" in response.content.decode()
        assert not Rule.objects.filter(security_group=group).exists()


class TestNetworkViews:
    def test_network_list(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        response = client.get(reverse("networks:network-list"))
        assert response.status_code == 200
        assert test_net.name.encode() in response.content
        assert test_net.cidr.encode() in response.content

    def test_network_detail(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        ca = CA.objects.create(network=test_net, name="test_ca")
        group = create_group(test_net.pk, "test_group")

        response = client.get(
            reverse("networks:network-detail", kwargs={"pk": test_net.id})
        )

        assert response.status_code == 200
        assert test_net.name.encode() in response.content
        assert test_net.cidr.encode() in response.content
        assert ca.name.encode() in response.content
        assert group.name.encode() in response.content

    @pytest.mark.parametrize(
        "test_data,expected_status",
        [
            ({"name": "test_net", "cidr": "192.168.1.0/24", "update_interval": 5}, 302),
            ({"name": "test_net", "cidr": "10.0.0.0/16", "update_interval": 5}, 302),
            ({"name": "test_net", "cidr": "100.64.0.0/24", "update_interval": 5}, 302),
            (
                {"name": "test_net", "cidr": "199.100.69.0/24", "update_interval": 5},
                200,
            ),
        ],
    )
    def test_network_cidr_validation(self, auth_client, test_data, expected_status):
        client, _ = auth_client()
        response = client.post(reverse("networks:network-create"), test_data)

        assert response.status_code == expected_status

        if expected_status == 302:
            assert Network.objects.filter(name=test_data["name"]).exists()
        else:
            assert not Network.objects.filter(name=test_data["name"]).exists()


class TestTemplateViews:
    def test_template_creation_with_security_group(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group1 = create_group(test_net.pk, "group1")
        group2 = create_group(test_net.pk, "group2")
        security_group = create_group(
            test_net.pk,
            "security_group",
            "Security group for testing",
        )
        Rule.objects.create(
            security_group=security_group,
            group=group1,
            direction="I",
            proto="tcp",
            port="80",
        )
        data = {
            "name": "test_template",
            "network": test_net.id,
            "is_lighthouse": False,
            "is_relay": False,
            "use_relay": True,
            "groups": [group1.id, group2.id, security_group.id],
        }
        response = client.post(
            reverse(
                "networks:network-template-create", kwargs={"network_id": test_net.id}
            ),
            data,
        )
        assert response.status_code == 302
        template = Template.objects.get(name="test_template")
        assert list(template.groups.all()) == [group1, group2, security_group]

    def test_template_deletion(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        security_group = create_group(
            test_net.pk, "test_security_group", "Test security group"
        )
        template = create_template(
            "test_template",
            test_net.name,
            groups=[security_group.name],
        )

        response = client.post(
            reverse("networks:template-delete", kwargs={"pk": template.id}),
        )

        assert response.status_code == 302
        assert not Template.objects.filter(id=template.id).exists()
        assert Group.objects.filter(id=security_group.id).exists()

    def test_template_creation_with_all_settings(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        data = {
            "name": "test_template_with_settings",
            "network": test_net.id,
            "is_lighthouse": False,
            "is_relay": False,
            "use_relay": True,
            "reusable": False,
            "usage_limit": 5,
            "expiry_days": 30,
            "ephemeral_peers": True,
        }

        response = client.post(
            reverse(
                "networks:network-template-create", kwargs={"network_id": test_net.id}
            ),
            data,
        )

        assert response.status_code == 302
        template = Template.objects.get(name="test_template_with_settings")
        assert template.reusable is False
        assert template.usage_limit == 5
        assert template.ephemeral_peers is True
        assert template.expires_at is not None

        # The expiry_days field should be converted to an expires_at datetime
        # Check that it's approximately 30 days in the future (within 1 day tolerance)
        expected_expiry = timezone.now() + timedelta(days=30)
        assert (
            abs((template.expires_at - expected_expiry).total_seconds()) < 86400
        )  # 1 day in seconds

    def test_template_update_with_enrollment_settings(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        template = create_template(
            "template_to_update",
            test_net.name,
            reusable=True,
            usage_limit=None,
            ephemeral_peers=False,
        )
        data = {
            "name": "updated_template",
            "network": test_net.id,
            "is_lighthouse": False,
            "is_relay": False,
            "use_relay": True,
            "reusable": False,
            "usage_limit": 10,
            "expiry_days": 15,
            "ephemeral_peers": True,
        }
        response = client.post(
            reverse("networks:template-edit", kwargs={"pk": template.id}),
            data,
        )
        assert response.status_code == 302
        template.refresh_from_db()
        assert template.name == "updated_template"
        assert template.reusable is False
        assert template.usage_limit == 10
        assert template.ephemeral_peers is True
        assert template.expires_at is not None

        # Check expiry date is approximately 15 days in the future
        expected_expiry = timezone.now() + timedelta(days=15)
        assert abs((template.expires_at - expected_expiry).total_seconds()) < 86400

    def test_template_update_remove_expiry(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        template = Template.objects.create(
            name="template_with_expiry",
            network=test_net,
            expires_at=timezone.now() + timedelta(days=30),
        )
        data = {
            "name": "template_without_expiry",
            "network": test_net.id,
            "is_lighthouse": False,
            "is_relay": False,
            "use_relay": True,
            "reusable": True,
            "usage_limit": "",  # Empty string for no limit
            "expiry_days": "",  # Empty string for no expiration
            "ephemeral_peers": False,
        }
        response = client.post(
            reverse("networks:template-edit", kwargs={"pk": template.id}),
            data,
        )
        assert response.status_code == 302
        template.refresh_from_db()
        assert template.name == "template_without_expiry"
        assert template.expires_at is None


class TestNetworkMembershipViews:
    def test_add_member(self, auth_client, test_network, create_user):
        client, admin_user = auth_client()
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=admin_user)
        new_member = create_user(email="member@example.com", username="member")
        url = reverse("networks:network-member-add", kwargs={"network_id": network.id})
        data = {
            "email": new_member.email,
            "role": "MEMBER",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        membership = network.memberships.get(user=new_member)
        assert membership.role == "MEMBER"

    def test_add_duplicate_member(self, auth_client, test_network, create_user):
        client, admin_user = auth_client()
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=admin_user)
        existing_member = create_user(email="member@example.com", username="member")
        network.memberships.create(user=existing_member, role="MEMBER")
        url = reverse("networks:network-member-add", kwargs={"network_id": network.id})
        data = {
            "email": existing_member.email,
            "role": "MEMBER",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert (
            "This user is already a member of the network" in response.content.decode()
        )

    def test_edit_member_role(self, auth_client, test_network, create_user):
        client, admin_user = auth_client()
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=admin_user)
        member = create_user(email="member@example.com", username="member")
        membership = network.memberships.create(user=member, role="MEMBER")
        url = reverse(
            "networks:network-member-edit",
            kwargs={"network_id": network.id, "pk": membership.pk},
        )
        headers = {"HX-Request": "true"}
        data = "role=ADMIN"
        response = client.put(
            url, data=data, content_type="application/x-www-form-urlencoded", **headers
        )
        assert response.status_code == 200
        membership.refresh_from_db()
        assert membership.role == "ADMIN"
        assert "membership-row-" in response.content.decode()

    def test_delete_member(self, auth_client, test_network, create_user):
        client, admin_user = auth_client()
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=admin_user)
        member = create_user(email="member@example.com", username="member")
        membership = network.memberships.create(user=member, role="MEMBER")
        url = reverse(
            "networks:network-member-delete",
            kwargs={"network_id": network.id, "pk": membership.pk},
        )
        headers = {"HX-Request": "true"}
        response = client.delete(url, **headers)
        assert response.status_code == 404
        assert not network.memberships.filter(pk=membership.pk).exists()

    def test_unauthorized_member_operations(
        self, auth_client, test_network, create_user
    ):
        client, _ = auth_client()
        admin_user = create_user(email="admin@example.com", username="admin")
        network = test_network(name="testnet", cidr="100.100.64.0/24", user=admin_user)
        member = create_user(email="member@example.com", username="member")
        membership = network.memberships.create(user=member, role="MEMBER")
        add_url = reverse(
            "networks:network-member-add", kwargs={"network_id": network.id}
        )
        response = client.post(add_url, {"email": "new@example.com", "role": "MEMBER"})
        assert response.status_code == 403
        edit_url = reverse(
            "networks:network-member-edit",
            kwargs={"network_id": network.id, "pk": membership.pk},
        )
        response = client.put(
            edit_url,
            data="role=ADMIN",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 403
        delete_url = reverse(
            "networks:network-member-delete",
            kwargs={"network_id": network.id, "pk": membership.pk},
        )
        response = client.delete(delete_url)
        assert response.status_code == 403


class TestGroupConfigViews:
    def test_add_config_to_group_success(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group_data = {"name": "test_group", "description": "Test group"}
        response = client.post(
            reverse(
                "networks:network-group-create", kwargs={"network_id": test_net.id}
            ),
            group_data,
        )
        assert response.status_code == 302
        group = Group.objects.get(name="test_group")
        config_data = {
            "group": group.id,
            "key": "lighthouse.serve_dns",
            "value": "true",
        }
        response = client.post(
            reverse("networks:group-add-config"),
            config_data,
        )
        assert response.status_code == 200
        assert GroupConfig.objects.filter(group=group).exists()
        config = GroupConfig.objects.get(group=group)
        assert config.key == "lighthouse.serve_dns"
        assert config.value == "true"

    def test_add_config_override_with_invalid_value(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        config_data = {
            "group": group.id,
            "key": "lighthouse.serve_dns",
            "value": "invalid_value",
        }
        response = client.post(
            reverse("networks:group-add-config"),
            config_data,
        )
        assert response.status_code == 200
        assert "Value must be a boolean (true/false)" in response.content.decode()

    def test_edit_config_override(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        config = GroupConfig.objects.create(
            group=group,
            key="lighthouse.serve_dns",
            value="true",
        )
        config_data = {
            "group": group.id,
            "config": config.id,
            "key": "lighthouse.serve_dns",
            "value": "false",
        }
        response = client.post(
            reverse("networks:group-add-config"),
            config_data,
        )
        assert response.status_code == 200
        config.refresh_from_db()
        assert config.value == "false"

    def test_delete_config_override(self, auth_client, test_network):
        client, user = auth_client()
        test_net = test_network(name="testnet", cidr="100.100.64.0/24", user=user)
        group = create_group(test_net.pk, "test_group")
        config = GroupConfig.objects.create(
            group=group,
            key="lighthouse.serve_dns",
            value="true",
        )
        response = client.delete(
            reverse("networks:group-config-delete", kwargs={"pk": config.id}),
        )
        assert response.status_code == 200
        assert not GroupConfig.objects.filter(id=config.id).exists()
