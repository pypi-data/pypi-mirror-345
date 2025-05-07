"""
Core API client for the WireGuard Configuration Distribution API.
"""

import time
from typing import Dict, List, Optional, Tuple

import requests


class WireGuardAPI:
    """Client for the WireGuard Configuration Distribution API."""

    def __init__(
        self,
        api_url: str,
        hashed_credential: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """
        Initialize the WireGuard API client.

        Args:
            api_url: Base URL for the API (e.g., "http://20.46.55.161:8080/api/v1")
            hashed_credential: Pre-hashed credential for authentication
            token: Existing JWT token (optional)
        """
        self.api_url = api_url.rstrip("/")
        self.hashed_credential = hashed_credential
        self.token = token
        self.token_expires_at = 0
        self.refresh_token = None  # Initialize refresh_token attribute

    def authenticate(self) -> Tuple[bool, str]:
        """
        Authenticate with the API and get a JWT token.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.hashed_credential:
            return False, "No hashed credential provided"

        url = f"{self.api_url}/auth/login"
        payload = {"hashed_credential": self.hashed_credential}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.refresh_token = data.get("refreshToken")
                # Set expiry time to 55 minutes from now (assuming 60 min token lifetime)
                self.token_expires_at = time.time() + (55 * 60)
                return True, "Authentication successful"
            else:
                return False, f"Authentication failed: {response.text}"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    def refresh_auth_token(self) -> Tuple[bool, str]:
        """
        Refresh the authentication token.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.refresh_token:
            return False, "No refresh token available"

        url = f"{self.api_url}/auth/refresh"
        payload = {"refresh_token": self.refresh_token}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.refresh_token = data.get("refreshToken")
                self.token_expires_at = time.time() + (55 * 60)
                return True, "Token refresh successful"
            else:
                return False, f"Token refresh failed: {response.text}"
        except Exception as e:
            return False, f"Token refresh error: {str(e)}"

    def ensure_authenticated(self) -> bool:
        """
        Ensure the client is authenticated, refreshing the token if needed.

        Returns:
            bool: True if authenticated, False otherwise
        """
        if not self.token or time.time() > self.token_expires_at:
            if self.refresh_token:
                success, _ = self.refresh_auth_token()
                if success:
                    return True

            success, _ = self.authenticate()
            return success
        return True

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers needed for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request_wireguard_config(
        self, device_id: str, role: str, public_key: str
    ) -> Tuple[bool, Dict]:
        """
        Request a WireGuard configuration for a device.

        Args:
            device_id: Unique identifier for the device
            role: Device role (either 'drone' or 'fmo')
            public_key: WireGuard public key

        Returns:
            Tuple of (success: bool, response_data: Dict)
        """
        if not self.ensure_authenticated():
            return False, {"error": "Authentication required"}

        url = f"{self.api_url}/wireguard/config"
        payload = {"device_id": device_id, "role": role, "public_key": public_key}

        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Request failed: {response.text}"}
        except Exception as e:
            return False, {"error": f"Request error: {str(e)}"}

    def list_devices(self) -> Tuple[bool, List[Dict]]:
        """
        List all registered devices (admin only).

        Returns:
            Tuple of (success: bool, devices: List[Dict])
        """
        if not self.ensure_authenticated():
            return False, []

        url = f"{self.api_url}/wireguard/devices"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                devices = response.json() or []
                return True, devices
            else:
                return False, []
        except Exception as e:
            print(f"Error listing devices: {e}")
            return False, []

    def get_device(self, device_id: str) -> Tuple[bool, Dict]:
        """
        Get information about a specific device (admin only).

        Args:
            device_id: ID of the device to retrieve

        Returns:
            Tuple of (success: bool, device_data: Dict)
        """
        if not self.ensure_authenticated():
            return False, {}

        url = f"{self.api_url}/wireguard/devices/{device_id}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {}
        except Exception as e:
            print(f"Error getting device: {e}")
            return False, {}

    def delete_device(self, device_id: str) -> Tuple[bool, str]:
        """
        Delete a specific device (admin only).

        Args:
            device_id: ID of the device to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ensure_authenticated():
            return False, "Authentication required"

        url = f"{self.api_url}/wireguard/devices/{device_id}"

        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return True, "Device deleted successfully"
            else:
                return False, f"Delete failed: {response.text}"
        except Exception as e:
            return False, f"Delete error: {str(e)}"

    def delete_all_devices(self) -> Tuple[bool, str]:
        """
        Delete all devices (admin only).

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ensure_authenticated():
            return False, "Authentication required"

        url = f"{self.api_url}/wireguard/devices"

        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return True, "All devices deleted successfully"
            else:
                return False, f"Delete failed: {response.text}"
        except Exception as e:
            return False, f"Delete error: {str(e)}"

    def get_fmo_device(self) -> Tuple[bool, Dict]:
        """
        Get the current FMO device (admin only).

        Returns:
            Tuple of (success: bool, device_data: Dict)
        """
        if not self.ensure_authenticated():
            return False, {}

        url = f"{self.api_url}/fmo/device"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {}
        except Exception as e:
            return False, f"Error getting FMO device: {str(e)}"

    def delete_fmo_role(self) -> Tuple[bool, str]:
        """
        Remove FMO role from current device (admin only).

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ensure_authenticated():
            return False, "Authentication required"

        url = f"{self.api_url}/fmo/device"

        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return True, "FMO role removed successfully"
            else:
                return False, f"Remove FMO role failed: {response.text}"
        except Exception as e:
            return False, f"Remove FMO role error: {str(e)}"

    def add_credential(self, hashed_credential: str, role: str) -> Tuple[bool, str]:
        """
        Add a new credential (admin only).

        Args:
            hashed_credential: Hashed credential to add
            role: Role for the credential ('user' or 'admin')

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ensure_authenticated():
            return False, "Authentication required"

        url = f"{self.api_url}/admin/credentials"
        payload = {"hashed_credential": hashed_credential, "role": role}

        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=10
            )
            if response.status_code == 201:
                return True, "Credential added successfully"
            else:
                return False, f"Add credential failed: {response.text}"
        except Exception as e:
            return False, f"Add credential error: {str(e)}"
