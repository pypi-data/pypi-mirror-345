"""
Tests for the WireGuard API client.
"""

import unittest
from unittest.mock import MagicMock, patch

from wg_api_client.api import WireGuardAPI


class TestWireGuardAPI(unittest.TestCase):
    """Test cases for the WireGuard API client."""

    def setUp(self):
        """Set up test fixtures."""
        self.api = WireGuardAPI(
            api_url="http://example.com/api",
            hashed_credential="test-credential",
        )

    @patch("requests.post")
    def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test-token",
            "refreshToken": "test-refresh-token",
        }
        mock_post.return_value = mock_response

        # Call method
        success, message = self.api.authenticate()

        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Authentication successful")
        self.assertEqual(self.api.token, "test-token")
        self.assertEqual(self.api.refresh_token, "test-refresh-token")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_authenticate_failure(self, mock_post):
        """Test failed authentication."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # Call method
        success, message = self.api.authenticate()

        # Assertions
        self.assertFalse(success)
        self.assertEqual(message, "Authentication failed: Unauthorized")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_refresh_auth_token_success(self, mock_post):
        """Test successful token refresh."""
        # Set up initial state
        self.api.refresh_token = "old-refresh-token"  # nosec B105

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "new-token",
            "refreshToken": "new-refresh-token",
        }
        mock_post.return_value = mock_response

        # Call method
        success, message = self.api.refresh_auth_token()

        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Token refresh successful")
        self.assertEqual(self.api.token, "new-token")
        self.assertEqual(self.api.refresh_token, "new-refresh-token")
        mock_post.assert_called_once()

    @patch("wg_api_client.api.WireGuardAPI.authenticate")
    def test_ensure_authenticated_no_token(self, mock_authenticate):
        """Test ensure_authenticated when no token exists."""
        # Set up initial state
        self.api.token = None
        mock_authenticate.return_value = (True, "Success")

        # Call method
        result = self.api.ensure_authenticated()

        # Assertions
        self.assertTrue(result)
        mock_authenticate.assert_called_once()

    @patch("requests.post")
    def test_request_wireguard_config_success(self, mock_post):
        """Test successful WireGuard config request."""
        # Set up initial state
        self.api.token = "test-token"  # nosec B105
        self.api.token_expires_at = 9999999999  # Far future

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "device_address": "10.0.0.2",
            "server_public_key": "test-server-key",
        }
        mock_post.return_value = mock_response

        # Call method
        success, data = self.api.request_wireguard_config(
            "test-device", "drone", "test-pubkey"
        )

        # Assertions
        self.assertTrue(success)
        self.assertEqual(data["device_address"], "10.0.0.2")
        self.assertEqual(data["server_public_key"], "test-server-key")
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
