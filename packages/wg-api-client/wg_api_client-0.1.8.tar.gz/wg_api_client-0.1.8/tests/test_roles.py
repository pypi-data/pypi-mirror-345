"""
Tests for device role functionality.
"""

import sys
import unittest

sys.path.append("..")

from wg_api_client import (
    AVAILABLE_ROLES,
    DEFAULT_ROLE,
    DEVICE_ROLES,
    get_role_description,
)


class TestDeviceRoles(unittest.TestCase):
    """Test cases for device role functionality."""

    def test_available_roles(self):
        """Test that available roles match the keys in DEVICE_ROLES."""
        self.assertEqual(set(AVAILABLE_ROLES), set(DEVICE_ROLES.keys()))
        self.assertTrue(
            all(role in AVAILABLE_ROLES for role in ["uxu", "drone", "fmo"])
        )

    def test_default_role(self):
        """Test that DEFAULT_ROLE is one of the available roles and is marked as default."""
        self.assertIn(DEFAULT_ROLE, AVAILABLE_ROLES)
        self.assertTrue(DEVICE_ROLES[DEFAULT_ROLE]["is_default"])

    def test_only_one_default_role(self):
        """Test that only one role is marked as default."""
        default_roles = [
            role for role, attrs in DEVICE_ROLES.items() if attrs.get("is_default")
        ]
        self.assertEqual(len(default_roles), 1)
        self.assertEqual(default_roles[0], DEFAULT_ROLE)

    def test_uxu_is_default(self):
        """Test that 'uxu' is the default role."""
        self.assertEqual(DEFAULT_ROLE, "uxu")

    def test_role_description(self):
        """Test the role description utility function."""
        # Test single role description
        uxu_desc = get_role_description("uxu")
        self.assertIn("UXU device", uxu_desc)
        self.assertIn("default", uxu_desc)

        # Test all roles description
        all_desc = get_role_description()
        self.assertIn("uxu", all_desc)
        self.assertIn("drone", all_desc)
        self.assertIn("fmo", all_desc)
        self.assertIn("default", all_desc)


if __name__ == "__main__":
    unittest.main()
