# Hetzner Network Setup Demo

This guide demonstrates how to set up a complete mesh network on Hetzner Cloud, including proper firewall configuration, lighthouse setup, and connecting multiple nodes.

## 1. Initial Network Setup

1. Log into your meshadmin web interface
2. Create a new network
3. Create a group with firewall rules (This will be used later to test connectivity)
   - Inbound Rules:
      - Port: any
      - Proto: icmp
      - CIDR: 0.0.0.0/0
   - Outbound Rules:
      - Port: any
      - Proto: any
      - CIDR: 0.0.0.0/0
4. Create two templates inside this network (one for the lighthouse and one for the node). Make sure to apply the group to the templates.

## 2. Hetzner Infrastructure Setup

### Base Firewall Rules

Create a new firewall with the following rules:

```
Inbound Rules:
- Allow TCP 22 (SSH)
- Allow UDP 4242 (Nebula Mesh Network)

Outbound Rules:
- Allow all
```

### Set Up Lighthouse Server

1. Create new server with the firewall applied.
2. SSH into the server and run:
   ```bash
   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env

   # Install MeshAdmin
   uv tool install --upgrade meshadmin

   # Configure lighthouse
   meshadmin context create default --endpoint <MESH_SERVER_URL>
   meshadmin host enroll <ENROLLMENT_KEY>
   meshadmin nebula start
   meshadmin service install
   meshadmin service start
   ```
   You can find the enrollment key on the lighthouse template detail page.

## 3. Additional Node Setup

1. Create second server with the firewall applied.

2. SSH into the server and run:
   ```bash
   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env

   # Install MeshAdmin
   uv tool install --upgrade meshadmin

   # Join mesh network
   meshadmin context create default --endpoint <MESH_SERVER_URL>
   meshadmin host enroll <ENROLLMENT_KEY>
   meshadmin nebula start
   meshadmin service install
   meshadmin service start
   ```
   You can find the enrollment key on the node template detail page.

## 4. Local Docker Setup

1. On your local machine, create a docker container
   ```bash
   docker run -d --name mesh-client \
   --cap-add=NET_ADMIN \
   --device=/dev/net/tun:/dev/net/tun \
   -p 4242:4242/udp \
   ubuntu:22.04 sleep infinity
   ```

2. Run the following commands:
   ```bash
   # Enter the container
   docker exec -it mesh-client bash

   # Install required packages
   apt update && apt install -y curl iputils-ping iproute2

   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env

   # Install MeshAdmin
   uv tool install --upgrade meshadmin

   # Join mesh network
   meshadmin context create default --endpoint <MESH_SERVER_URL>
   meshadmin host enroll <ENROLLMENT_KEY>
   meshadmin nebula start
   ```

## 5. Testing Connectivity

Test network connectivity between all nodes:
   ```bash
   # From lighthouse to node-1
   ping <node-1-mesh-ip>

   # From node-1 to lighthouse
   ping <lighthouse-mesh-ip>

   # From Docker container to both nodes
   ping <lighthouse-mesh-ip>
   ping <node-1-mesh-ip>

   # From node-1 to Docker container
   ping <docker-mesh-ip>

   # From lighthouse to Docker container
   ping <docker-mesh-ip>
   ```
