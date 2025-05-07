# Meshadmin
A simple admin interface for the nebula mesh.

Allows to administer multiple networks.

## Documentation

- [Installation and Basic Usage](#installation)
- [Release Process](#release)
- [Hetzner Cloud Setup Demo](docs/hetzner-demo.md)

## Installation
###  Setup CLI on host
```bash
# Install Curl
apt install curl

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to your current shell session
source $HOME/.local/bin/env

# Install meshadmin package
uv tool install meshadmin
```

### Usage
```bash
# Create a context
meshadmin context create default --endpoint <MESH_SERVER_URL>

# Enroll a new host
meshadmin host enroll <ENROLLMENT_KEY>

# Start process for config updates
meshadmin nebula start

# Install as a service
meshadmin service install

# Start service
meshadmin service start

# Other commands
meshadmin --help
```


## Release

We use [**Hatch VCS**](https://github.com/ofek/hatch-vcs) to manage versions dynamically based on Git tags and commits. Stable releases are deployed to PyPI when a Git tag is pushed, while development versions are used for testing.

### **1. Development Versions**

- Development versions are generated dynamically from Git commits.
- They follow the format: `0.1.dev<N>` (e.g., `0.1.dev20`).

### **Stable Releases**

- A stable release is triggered by pushing an **annotated Git tag**.
- Follow SemVer, e.g., `v0.2.0`.
- The CI/CD pipeline automatically detects the tag and releases the package to PyPI.

### Releasing a Stable Version:

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

- After the pipeline is completed, the package will be available at:
    - **PyPI**: https://pypi.org/project/meshadmin/
