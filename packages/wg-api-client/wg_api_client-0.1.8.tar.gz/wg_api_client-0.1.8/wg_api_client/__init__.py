"""
WireGuard Configuration API Client

A comprehensive client library and CLI tool for interacting with the
WireGuard Configuration Distribution API.
"""

__version__ = "0.1.8"

# Device roles
DEVICE_ROLES = {
    "uxu": {"description": "UXU device", "is_default": True},
    "drone": {"description": "Drone device", "is_default": False},
    "fmo": {"description": "Field Management Operator device", "is_default": False},
    # New roles should be added here
}

# Get the default role
DEFAULT_ROLE = next(
    (role for role, attrs in DEVICE_ROLES.items() if attrs.get("is_default")), "uxu"
)

# Get all available roles
AVAILABLE_ROLES = list(DEVICE_ROLES.keys())


# Utility function to generate role documentation
def get_role_description(role=None):
    """
    Get description for a specific role or all roles.

    Args:
        role: Role name or None for all roles

    Returns:
        String with role description(s)
    """
    if role is not None:
        attrs = DEVICE_ROLES.get(role, {})
        desc = attrs.get("description", "Unknown role")
        if attrs.get("is_default"):
            desc += " (default)"
        return desc

    # Return descriptions for all roles
    descriptions = []
    for r, attrs in DEVICE_ROLES.items():
        desc = f"{r}: {attrs.get('description', '')}"
        if attrs.get("is_default"):
            desc += " (default)"
        descriptions.append(desc)

    return ", ".join(descriptions)


__all__ = [
    "WireGuardAPI",
    "ConfigManager",
    "WireGuardHelper",
    "DEVICE_ROLES",
    "DEFAULT_ROLE",
    "AVAILABLE_ROLES",
    "get_role_description",
]
