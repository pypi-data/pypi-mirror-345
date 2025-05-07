# WireGuard Configuration API Client

A comprehensive client library and CLI tool for interacting with the WireGuard Configuration Distribution API.

[![CI](https://github.com/tiiuae/wg-api-client-lib/actions/workflows/ci.yml/badge.svg)](https://github.com/tiiuae/wg-api-client-lib/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/wg-api-client.svg)](https://pypi.org/project/wg-api-client/)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Configuration Options](#configuration-options)
- [Common Workflows](#common-workflows)
- [Device Roles](#device-roles)
- [Device ID Generation](#device-id-generation)
- [Using as a Library](#using-as-a-library)
- [Development](#development)
- [Publishing](#publishing)
- [License](#license)

## Features

- Complete API client for the WireGuard Configuration Distribution API
- Command-line interface for all API operations
- Automatic token authentication and renewal
- Configuration file support
- WireGuard keypair generation
- WireGuard configuration file creation
- Hardware-based device ID generation for reliable device identification
- Custom device ID support for greater flexibility
- Support for custom routing tables and AllowedIPs in WireGuard configurations
- Multiple device roles (uxu, drone, fmo) with expandable architecture

## Installation

### From PyPI (Recommended)

```bash
pip install wg-api-client
```

### From Source

```bash
git clone https://github.com/tiiuae/wg-api-client-lib.git
cd wg-api-client-lib
pip install -e .
```

### Prerequisites

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip wireguard-tools
```

#### Fedora/CentOS/RHEL

```bash
sudo dnf install python3 python3-pip wireguard-tools
```

## Quick Start

```bash
# Install the package
pip install wg-api-client

# Authenticate with the API
wg-api-client auth

# Get a WireGuard configuration file
wg-api-client get-config --output my-device.conf

# Apply the configuration
sudo wg-quick up my-device.conf
```

## Command Reference

### Global Parameters

These parameters can be used with any command:

```
--api-url URL         Base URL for the API
--hashed-credential HASH  Hashed credential for authentication
--config-file PATH    Path to configuration file (default: ~/.wg_api_config)
```

### Authentication

```bash
wg-api-client auth
```

Authenticates with the API using the provided or configured hashed credential.

### Device Configuration

```bash
wg-api-client get-config [OPTIONS]
```

Options:
- `--role {uxu|drone|fmo}` - Device role (default: uxu)
- `--device-id ID` - Custom device ID (generated from hardware if not provided)
- `--public-key KEY` - WireGuard public key (generated if not provided)
- `--output FILE` - Output configuration file (default: wg.conf)
- `--allowed-ips CIDR` - Additional IP ranges to allow (can be used multiple times)
- `--table NAME` or `-t NAME` - Set routing table for the WireGuard interface

### Device Management (Admin only)

```bash
# List all devices
wg-api-client list-devices

# Get information about a specific device
wg-api-client get-device DEVICE_ID

# Delete a device
wg-api-client delete-device DEVICE_ID

# Delete all devices
wg-api-client delete-all-devices [--confirm]
```

### FMO Management (Admin only)

```bash
# Get current FMO device
wg-api-client get-fmo

# Remove FMO role from current device
wg-api-client delete-fmo
```

### Credential Management (Admin only)

```bash
# Add a new credential
wg-api-client add-credential --hashed-credential HASH [--role {user|admin}]
```

## Configuration Options

### Configuration File

The tool stores configuration in `~/.wg_api_config` by default. This includes:
- API URL
- Hashed credential
- Authentication token
- Refresh token

To specify a different configuration file location:

```bash
wg-api-client --config-file /path/to/config [command]
```

### WireGuard Configuration Options

When generating a WireGuard configuration file, you can customize:

1. **Device role** (`--role`): uxu, drone, or fmo
2. **Device ID** (`--device-id`): Use a custom identifier or auto-generate
3. **WireGuard keypair** (`--public-key`): Provide an existing public key or auto-generate
4. **Allowed IPs** (`--allowed-ips`): Add custom IP ranges beyond the default (10.8.0.0/24)
5. **Routing table** (`--table` or `-t`): Specify a custom routing table name

Example with all options:

```bash
wg-api-client get-config \
  --role drone \
  --device-id "drone-inspection-5" \
  --public-key "AbCdEf123..." \
  --allowed-ips 192.168.128.0/24 \
  --allowed-ips 172.16.0.0/16 \
  --table internet \
  --output drone-5.conf
```

## Common Workflows

### Basic Device Setup

```bash
# Authenticate
wg-api-client auth

# Generate config for a UXU device (default role)
wg-api-client get-config --output uxu.conf

# Apply configuration
sudo wg-quick up uxu.conf
```

### Drone Device with Custom ID

```bash
# Generate configuration with descriptive ID
wg-api-client get-config \
  --role drone \
  --device-id "drone-inspection-team-1" \
  --output drone-team1.conf
```

### FMO Device with Custom Routing Table

```bash
# Generate FMO configuration with custom routing table
wg-api-client get-config \
  --role fmo \
  --device-id "fmo-ground-station" \
  --table internet \
  --output fmo.conf
```

### Administrator Tasks

```bash
# Check all registered devices
wg-api-client list-devices

# Add a new admin credential
wg-api-client add-credential --hashed-credential "your-hashed-credential" --role admin

# Clean up old devices
wg-api-client delete-device old-device-id

# Set up a new FMO (removing previous one if needed)
wg-api-client get-fmo
wg-api-client delete-fmo
wg-api-client get-config --role fmo --output new-fmo.conf
```

## Device Roles

The client supports multiple device roles:

- **uxu**: Default role for UXU devices
- **drone**: For drone devices
- **fmo**: For Field Management Operator devices (only one can be active)

Each role may have different capabilities and network access within the WireGuard setup.

## Device ID Generation

### Custom Device ID

Using a custom device ID with the `--device-id` parameter offers:
- More descriptive names for easier management
- Alignment with your organization's naming conventions
- Better tracking across deployments
- Independence from hardware changes

### Auto-generated ID

When no custom ID is provided, the client generates a unique ID based on hardware information:
1. Network interface MAC addresses
2. Machine UUID from OS-specific sources
3. Other machine-specific information

This ensures a stable, unique identifier that persists across reboots.

## Using as a Library

```python
from wg_api_client import WireGuardAPI, WireGuardHelper, DEFAULT_ROLE
from wg_api_client.unique_id import get_unique_device_id

# Initialize the API client
api = WireGuardAPI(
    api_url="your-api-url",
    hashed_credential="your-hashed-credential"
)

# Authenticate
api.authenticate()

# Generate a device ID
device_id = get_unique_device_id()

# Generate a keypair
private_key, public_key = WireGuardHelper.generate_keypair()

# Request configuration
success, config_data = api.request_wireguard_config(
    device_id=device_id,
    role="drone",
    public_key=public_key
)

if success:
    # Create configuration with additional options
    additional_allowed_ips = ["192.168.128.0/24"]
    routing_table = "internet"
    
    WireGuardHelper.create_client_config(
        config_data, 
        "drone.conf", 
        additional_allowed_ips, 
        routing_table
    )
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/tiiuae/wg-api-client-lib.git
cd wg-api-client-lib

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Run Tests

```bash
pytest
```

### Run Linters

```bash
# Format code with Black
black .

# Sort imports
isort .
```

### Project Structure

```
wg_api_client/
├── __init__.py   # Package initialization and version
├── __main__.py   # CLI entry point
├── api.py        # WireGuard API client
├── cli.py        # Command-line interface
├── config.py     # Configuration management
├── helper.py     # WireGuard utilities
└── unique_id.py  # Device ID generation
```

## Publishing

### Automatic Publishing

1. Update version in `wg_api_client/__init__.py` and `setup.py`
2. Create a GitHub release with tag `v{version}` (e.g., `v0.1.2`)
3. GitHub Actions will automatically build and publish to PyPI

### Manual Publishing

For detailed instructions on manual publishing, see [PUBLISHING.md](PUBLISHING.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.