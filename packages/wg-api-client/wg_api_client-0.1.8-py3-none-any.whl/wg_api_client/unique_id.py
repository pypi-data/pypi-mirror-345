#!/usr/bin/env python3
import logging
import os
import platform
import re
import socket
import subprocess  # nosec B404
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_eth0_mac():
    """Return the MAC address for eth0 on Linux, if it exists."""
    eth0_path = "/sys/class/net/eth0/address"
    if os.path.exists(eth0_path):
        try:
            with open(eth0_path, "r") as f:
                mac = f.read().strip()
                if mac and mac != "00:00:00:00:00:00":
                    logger.info("Found eth0 MAC address")
                    return mac
        except Exception as e:
            logger.error(f"Error reading eth0 MAC: {e}")
    return None


def get_primary_interface_mac():
    """Get MAC address of the primary network interface."""
    try:
        # Get the primary interface name (the one used for default route)
        if platform.system() == "Linux":
            with open("/proc/net/route", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if parts[1] == "00000000":  # Default route
                        interface = parts[0]
                        path = f"/sys/class/net/{interface}/address"
                        if os.path.exists(path):
                            with open(path, "r") as f:
                                mac = f.read().strip()
                                if mac and mac != "00:00:00:00:00:00":
                                    logger.info(
                                        f"Found primary interface ({interface}) MAC address"
                                    )
                                    return mac
        # For other platforms, we'll rely on get_first_mac()
    except Exception as e:
        logger.error(f"Error finding primary interface MAC: {e}")
    return None


def get_all_network_interfaces():
    """Get a list of all network interfaces and their MAC addresses."""
    interfaces = {}
    try:
        if platform.system() == "Linux":
            net_path = "/sys/class/net/"
            for interface in os.listdir(net_path):
                # Skip loopback and virtual interfaces
                if (
                    interface == "lo"
                    or interface.startswith("vir")
                    or interface.startswith("docker")
                ):
                    continue
                path = os.path.join(net_path, interface, "address")
                if os.path.exists(path):
                    with open(path, "r") as f:
                        mac = f.read().strip()
                        if mac and mac != "00:00:00:00:00:00":
                            interfaces[interface] = mac
        elif platform.system() == "Windows":
            output = subprocess.check_output(
                "getmac /v /fo csv", shell=True, universal_newlines=True
            )  # nosec B602, B607
            for line in output.splitlines()[1:]:  # Skip header
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    interface = parts[0].strip('"')
                    mac = parts[2].strip('"')
                    if mac and mac != "00:00:00:00:00:00":
                        interfaces[interface] = mac
        elif platform.system() == "Darwin":  # macOS
            output = subprocess.check_output(
                "ifconfig", shell=True, universal_newlines=True
            )  # nosec B602, B607
            current_interface = None
            for line in output.splitlines():
                if ":" in line and "mtu" in line.lower():
                    current_interface = line.split(":")[0]
                elif current_interface and "ether" in line.lower():
                    mac = line.split()[1].strip()
                    if mac and mac != "00:00:00:00:00:00":
                        interfaces[current_interface] = mac
    except Exception as e:
        logger.error(f"Error getting all network interfaces: {e}")

    logger.info(f"Found {len(interfaces)} network interfaces")
    return interfaces


def get_first_mac():
    """Use uuid.getnode() to get a MAC address."""
    try:
        node = uuid.getnode()
        # Check if the node is valid (not a random value)
        if (
            node != uuid.getnode()
        ):  # If called twice and returns different values, it's random
            logger.warning("uuid.getnode() returned potentially random value")
            return None

        # Format the node as a MAC address:
        mac = ":".join(f"{(node >> i) & 0xFF:02x}" for i in range(40, -1, -8))
        if mac and mac != "00:00:00:00:00:00":
            logger.info("Found MAC address using uuid.getnode()")
            return mac
    except Exception as e:
        logger.error(f"Error getting MAC with uuid.getnode(): {e}")
    return None


def get_machine_uuid():
    """Attempt to fetch a machine UUID using OS-specific commands."""
    system = platform.system()

    if system == "Linux":
        # Try the sysfs interface first (most reliable)
        paths = [
            "/sys/class/dmi/id/product_uuid",
            "/sys/class/dmi/id/board_uuid",
            "/etc/machine-id",
        ]

        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        uuid_str = f.read().strip()
                        if (
                            uuid_str
                            and len(uuid_str) > 8
                            and uuid_str != "03000200-0400-0500-0006-000700080009"
                        ):
                            logger.info(f"Found machine UUID from {path}")
                            return uuid_str
                except Exception as e:
                    logger.error(f"Error reading {path}: {e}")

        # Fallback using dmidecode (requires root)
        try:
            output = subprocess.check_output(
                "dmidecode -s system-uuid",
                shell=False,
                executable="/bin/bash",
                stderr=subprocess.DEVNULL,
                universal_newlines=True,
            )  # nosec B603, B607
            uuid_str = output.strip()
            if (
                uuid_str and uuid_str != "03000200-0400-0500-0006-000700080009"
            ):  # Common dummy/default UUID
                logger.info("Found machine UUID using dmidecode")
                return uuid_str
        except Exception as e:
            logger.error(f"Error with dmidecode: {e}")

    elif system == "Windows":
        try:
            # Try multiple commands for reliability
            commands = [
                "wmic csproduct get UUID",
                'powershell -Command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"',
            ]

            for cmd in commands:
                try:
                    output = subprocess.check_output(
                        cmd,
                        shell=True,
                        stderr=subprocess.DEVNULL,
                        universal_newlines=True,
                    )  # nosec B602
                    lines = output.splitlines()
                    for line in lines:
                        line = line.strip()
                        if line and line.lower() != "uuid" and len(line) > 8:
                            logger.info(f"Found Windows UUID using {cmd.split()[0]}")
                            return line
                except subprocess.CalledProcessError as e:
                    logger.error(f"Command '{cmd}' failed: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting Windows UUID: {e}")

    elif system == "Darwin":  # macOS
        try:
            # Try multiple commands for reliability
            commands = [
                "ioreg -rd1 -c IOPlatformExpertDevice | grep -i 'IOPlatformUUID'",
                "system_profiler SPHardwareDataType | grep -i 'Hardware UUID'",
            ]

            for cmd in commands:
                try:
                    output = subprocess.check_output(
                        cmd,
                        shell=True,
                        stderr=subprocess.DEVNULL,
                        universal_newlines=True,
                    )  # nosec B602
                    match = re.search(
                        r'["]?([0-9A-F]{8}(-[0-9A-F]{4}){3}-[0-9A-F]{12})["]?',
                        output,
                        re.IGNORECASE,
                    )
                    if match:
                        logger.info(f"Found macOS UUID using {cmd.split()[0]}")
                        return match.group(1)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Command '{cmd}' failed: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting macOS UUID: {e}")

    # Fallback to a hash of hostname + platform info if no UUID available
    try:
        unique_str = f"{socket.gethostname()}-{platform.node()}-{platform.platform()}"
        fallback_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, unique_str)
        logger.warning("Using fallback UUID based on hostname and platform")
        return str(fallback_uuid)
    except Exception as e:
        logger.error(f"Error creating fallback UUID: {e}")

    # Last resort fallback
    return str(uuid.uuid4())


def format_device_id(id_type, value):
    """Format the device ID into a compact hex representation with hex prefix."""
    # Define hex prefixes for different source types
    prefix_map = {
        "MAC-ETH0": "e0",  # e0 for eth0
        "MAC-PRIMARY": "01",  # 01 for primary interface
        "MAC-GENERIC": "02",  # 02 for generic MAC
        "UUID": "aa",  # aa for UUID
        "FALLBACK": "ff",  # ff for fallback
    }

    # Get the appropriate prefix or use a default
    prefix = prefix_map.get(id_type, "cc")  # cc as default for custom interfaces

    if "MAC" in id_type:
        # Convert MAC address to a compact representation
        mac_hex = value.replace(":", "").lower()
        return f"{prefix}{mac_hex[:8]}"
    elif "UUID" in id_type:
        # Take first 8 chars of UUID (stripping hyphens)
        uuid_hex = value.replace("-", "").lower()
        return f"{prefix}{uuid_hex[:8]}"
    else:
        # Fallback - hash the value to 8 hex chars
        import hashlib

        hash_val = hashlib.sha256(value.encode()).hexdigest()[:8]
        return f"{prefix}{hash_val}"


def get_unique_device_id():
    """
    Get a unique device ID:
    Priority 1: eth0 MAC address (if exists on Linux)
    Priority 2: Primary network interface MAC address
    Priority 3: Any available physical network interface MAC address
    Priority 4: MAC address from uuid.getnode()
    Priority 5: Machine UUID from OS-specific sources
    Priority 6: Fallback to machine-specific information

    Returns a 10-character hex string: 2-char type prefix + 8-char identifier
    """
    # Priority 1: Try eth0 (Linux)
    eth0_mac = get_eth0_mac()
    if eth0_mac:
        return format_device_id("MAC-ETH0", eth0_mac)

    # Priority 2: Primary network interface
    primary_mac = get_primary_interface_mac()
    if primary_mac:
        return format_device_id("MAC-PRIMARY", primary_mac)

    # Priority 3: Any physical network interface
    interfaces = get_all_network_interfaces()
    if interfaces:
        # Prefer ethernet interfaces over wireless ones
        for interface, mac in interfaces.items():
            if (
                interface.startswith(("eth", "en"))
                and "virtual" not in interface.lower()
            ):
                return format_device_id(f"MAC-{interface.upper()}", mac)
        # Otherwise, use the first one
        interface, mac = next(iter(interfaces.items()))
        return format_device_id(f"MAC-{interface.upper()}", mac)

    # Priority 4: Get any MAC address
    mac = get_first_mac()
    if mac:
        return format_device_id("MAC-GENERIC", mac)

    # Priority 5: Fallback to machine UUID
    machine_uuid = get_machine_uuid()
    if machine_uuid:
        return format_device_id("UUID", machine_uuid)

    # Priority 6: Ultimate fallback
    logger.warning("Using fallback random UUID - this will change between runs")
    return format_device_id("FALLBACK", str(uuid.uuid4()))


if __name__ == "__main__":
    try:
        unique_id = get_unique_device_id()
        print("Unique Device ID:", unique_id)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"Error obtaining unique ID: {e}")
