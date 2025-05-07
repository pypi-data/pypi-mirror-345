"""
Configuration management for the WireGuard API client.
"""

import configparser
import os
from typing import Optional


class ConfigManager:
    """Manage configuration settings for the WireGuard API client."""

    def __init__(self, config_file: str = "~/.wg_api_config"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = os.path.expanduser(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self) -> bool:
        """
        Load configuration from file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
                return True
            return False
        except Exception:
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                self.config.write(f)

            # Set appropriate permissions
            os.chmod(self.config_file, 0o600)
            return True
        except Exception:
            return False

    def get_api_url(self) -> str:
        """Get the API URL from configuration."""
        if "General" in self.config and "api_url" in self.config["General"]:
            return self.config["General"]["api_url"]
        return "http://20.46.55.161:8080/api/v1"  # Default value

    def set_api_url(self, url: str) -> None:
        """Set the API URL in configuration."""
        if "General" not in self.config:
            self.config["General"] = {}
        self.config["General"]["api_url"] = url

    def get_hashed_credential(self) -> Optional[str]:
        """Get the hashed credential from configuration."""
        if "Auth" in self.config and "hashed_credential" in self.config["Auth"]:
            return self.config["Auth"]["hashed_credential"]
        return None

    def set_hashed_credential(self, credential: str) -> None:
        """Set the hashed credential in configuration."""
        if "Auth" not in self.config:
            self.config["Auth"] = {}
        self.config["Auth"]["hashed_credential"] = credential

    def get_token(self) -> Optional[str]:
        """Get the JWT token from configuration."""
        if "Auth" in self.config and "token" in self.config["Auth"]:
            return self.config["Auth"]["token"]
        return None

    def set_token(self, token: str) -> None:
        """Set the JWT token in configuration."""
        if "Auth" not in self.config:
            self.config["Auth"] = {}
        self.config["Auth"]["token"] = token

    def get_refresh_token(self) -> Optional[str]:
        """Get the refresh token from configuration."""
        if "Auth" in self.config and "refresh_token" in self.config["Auth"]:
            return self.config["Auth"]["refresh_token"]
        return None

    def set_refresh_token(self, token: str) -> None:
        """Set the refresh token in configuration."""
        if "Auth" not in self.config:
            self.config["Auth"] = {}
        self.config["Auth"]["refresh_token"] = token

    def get_token_expires_at(self) -> int:
        """Get the token expiry timestamp from configuration."""
        if "Auth" in self.config and "token_expires_at" in self.config["Auth"]:
            return int(self.config["Auth"]["token_expires_at"])
        return 0

    def set_token_expires_at(self, timestamp: int) -> None:
        """Set the token expiry timestamp in configuration."""
        if "Auth" not in self.config:
            self.config["Auth"] = {}
        self.config["Auth"]["token_expires_at"] = str(timestamp)
