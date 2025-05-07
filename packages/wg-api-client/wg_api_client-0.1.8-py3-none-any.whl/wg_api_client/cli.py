"""
Command-line interface for the WireGuard API client.
"""

import argparse
import sys

from wg_api_client import AVAILABLE_ROLES, DEFAULT_ROLE, get_role_description
from wg_api_client.api import WireGuardAPI
from wg_api_client.config import ConfigManager
from wg_api_client.helper import WireGuardHelper
from wg_api_client.unique_id import get_unique_device_id


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="WireGuard Configuration API Client")

    # Global arguments
    parser.add_argument(
        "--api-url",
        default="http://20.46.55.161:8080/api/v1",
        help="Base URL for the API",
    )
    parser.add_argument(
        "--hashed-credential",
        default="55f914f38e716cde0b8eadfa2441dda31200a879b27d160a7bb1e5084663f349",
        help="Hashed credential for authentication",
    )
    parser.add_argument(
        "--config-file", default="~/.wg_api_config", help="Path to configuration file"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Authentication
    subparsers.add_parser("auth", help="Authenticate with the API")  # noqa: F841

    # Get WireGuard configuration
    config_parser = subparsers.add_parser(
        "get-config", help="Get WireGuard configuration with auto-generated device ID"
    )
    config_parser.add_argument(
        "--role",
        choices=AVAILABLE_ROLES,
        default=DEFAULT_ROLE,
        help=f"Device role (default: {DEFAULT_ROLE}). Available roles: {get_role_description()}",
    )
    config_parser.add_argument(
        "--device-id", help="Custom device ID (generated from hardware if not provided)"
    )
    config_parser.add_argument(
        "--public-key", help="WireGuard public key (generated if not provided)"
    )
    config_parser.add_argument(
        "--output", default="wg.conf", help="Output configuration file"
    )
    config_parser.add_argument(
        "--allowed-ips",
        action="append",
        help="Additional IP ranges to allow (can be used multiple times). Default range 10.8.0.0/24 is always included.",
    )
    config_parser.add_argument(
        "--table", "-t", help="Routing table for WireGuard interface (e.g. 'internet')"
    )

    # List devices
    subparsers.add_parser(
        "list-devices", help="List all devices (admin only)"
    )  # noqa: F841

    # Get device
    get_parser = subparsers.add_parser(
        "get-device", help="Get device information (admin only)"
    )
    get_parser.add_argument("device_id", help="Device ID")

    # Delete device
    delete_parser = subparsers.add_parser(
        "delete-device", help="Delete a device (admin only)"
    )
    delete_parser.add_argument("device_id", help="Device ID")

    # Delete all devices
    delete_all_parser = subparsers.add_parser(
        "delete-all-devices", help="Delete all devices (admin only)"
    )
    delete_all_parser.add_argument(
        "--confirm", action="store_true", help="Confirm deletion"
    )

    # Get FMO device
    subparsers.add_parser(
        "get-fmo", help="Get FMO device information (admin only)"
    )  # noqa: F841

    # Delete FMO role
    subparsers.add_parser(
        "delete-fmo", help="Remove FMO role (admin only)"
    )  # noqa: F841

    # Add credential
    add_cred_parser = subparsers.add_parser(
        "add-credential", help="Add a new credential (admin only)"
    )
    add_cred_parser.add_argument(
        "--hashed-credential", required=True, help="Hashed credential to add"
    )
    add_cred_parser.add_argument(
        "--role",
        choices=["user", "admin"],
        default="user",
        help="Role for the credential",
    )

    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    # Load configuration
    config_manager = ConfigManager(args.config_file)

    # Override configuration with command line arguments
    if args.api_url:
        config_manager.set_api_url(args.api_url)
    if args.hashed_credential:
        config_manager.set_hashed_credential(args.hashed_credential)

    # Initialize API client
    api = WireGuardAPI(
        api_url=config_manager.get_api_url(),
        hashed_credential=config_manager.get_hashed_credential(),
        token=config_manager.get_token(),
    )

    # Process command
    if args.command == "auth":
        success, message = api.authenticate()
        if success:
            # Save token to configuration
            config_manager.set_token(api.token)
            config_manager.set_refresh_token(getattr(api, "refresh_token", ""))
            config_manager.set_token_expires_at(int(api.token_expires_at))
            config_manager.save_config()
            print("Authentication successful")
        else:
            print(f"Authentication failed: {message}")
            return 1

    elif args.command == "get-config":
        if args.device_id:
            device_id = args.device_id
            print(f"Using provided device ID: {device_id}")
        else:
            # Generate device ID from hardware information
            device_id = get_unique_device_id()
            print(f"Generated hardware-based device ID: {device_id}")

        # Get or generate public key
        public_key = args.public_key
        using_local_keypair = False

        if not public_key:
            private_key, public_key = WireGuardHelper.generate_keypair()
            if not public_key:
                print("Failed to generate WireGuard key pair")
                return 1
            print("Generated WireGuard key pair for registration")
            print(f"Public key: {public_key}")
            using_local_keypair = True

        # Request configuration
        success, data = api.request_wireguard_config(device_id, args.role, public_key)

        if success:
            print("WireGuard configuration retrieved successfully")

            # Create configuration file
            success, message = WireGuardHelper.create_client_config(
                data, args.output, args.allowed_ips, args.table
            )
            print(message)

            # Print configuration summary
            if success:
                allowed_ips = ["10.8.0.0/24"]  # Default is always included
                if args.allowed_ips:
                    allowed_ips.extend(args.allowed_ips)

                print("\nConfiguration Summary:")
                print(f"  Device ID: {device_id}")
                print(f"  Role: {args.role}")
                print(f"  IP Address: {data.get('device_address')}")
                print(f"  Allowed IPs: {', '.join(allowed_ips)}")
                print(f"  FMO Address: {data.get('fmo_address', 'Not available')}")
                if args.table:
                    print(f"  Routing Table: {args.table}")
                print(f"  Configuration File: {args.output}")

    elif args.command == "list-devices":
        success, devices = api.list_devices()
        if success:
            print("Devices:")
            for device in devices:
                print(f"  ID: {device.get('id')}")
                print(f"    Role: {device.get('role')}")
                print(f"    IP: {device.get('ip')}")
                print(f"    Public Key: {device.get('public_key')}")
                print(f"    Created: {device.get('created_at')}")
                print(f"    Updated: {device.get('updated_at')}")
                print()
        else:
            print("Failed to list devices")
            return 1

    elif args.command == "get-device":
        success, device = api.get_device(args.device_id)
        if success:
            print(f"Device: {args.device_id}")
            print(f"  Role: {device.get('role')}")
            print(f"  IP: {device.get('ip')}")
            print(f"  Public Key: {device.get('public_key')}")
            print(f"  Created: {device.get('created_at')}")
            print(f"  Updated: {device.get('updated_at')}")
        else:
            print(f"Failed to get device: {args.device_id}")
            return 1

    elif args.command == "delete-device":
        success, message = api.delete_device(args.device_id)
        print(message)
        if not success:
            return 1

    elif args.command == "delete-all-devices":
        if not args.confirm:
            confirm = input("Are you sure you want to delete all devices? [y/N] ")
            if confirm.lower() != "y":
                print("Operation cancelled")
                return 0

        success, message = api.delete_all_devices()
        print(message)
        if not success:
            return 1

    elif args.command == "get-fmo":
        success, device = api.get_fmo_device()
        if success:
            print("FMO Device:")
            print(f"  ID: {device.get('id')}")
            print(f"  IP: {device.get('ip')}")
            print(f"  Public Key: {device.get('public_key')}")
            print(f"  Created: {device.get('created_at')}")
            print(f"  Updated: {device.get('updated_at')}")
        else:
            print("No FMO device found or error retrieving FMO device information")
            return 1

    elif args.command == "delete-fmo":
        success, message = api.delete_fmo_role()
        print(message)
        if not success:
            return 1

    elif args.command == "add-credential":
        success, message = api.add_credential(args.hashed_credential, args.role)
        print(message)
        if not success:
            return 1

    else:
        # No command specified, print usage
        print("No command specified. Use --help to see available commands.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
