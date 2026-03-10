"""
Instagram Business OAuth 2.0 Authentication Module
Handles token exchange, refresh, and credential management for Instagram Business API
"""

import os
import json
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from pathlib import Path


class InstagramAuthError(Exception):
    """Base exception for Instagram authentication errors"""
    def __init__(self, error_type: str, message: str, details: Optional[Dict] = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(f"{error_type}: {message}")


class InstagramAuth:
    """
    Instagram Business Authentication Manager
    Handles OAuth 2.0 flow, token management, and credential storage
    """

    GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "instagram_logs.json"

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        """
        Initialize Instagram Auth Manager

        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            redirect_uri: OAuth redirect URI
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

        # Ensure log directory exists
        self.LOG_DIR.mkdir(exist_ok=True)
        if not self.LOG_FILE.exists():
            self.LOG_FILE.write_text("[]")

    def _log_operation(self, operation: str, input_data: Dict, response_data: Dict, status: str):
        """
        Log all operations to audit log

        Args:
            operation: Name of the operation
            input_data: Input parameters
            response_data: API response or error details
            status: success or error
        """
        try:
            # Read existing logs
            logs = json.loads(self.LOG_FILE.read_text())

            # Append new log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "operation": operation,
                "input": input_data,
                "response": response_data,
                "status": status
            }
            logs.append(log_entry)

            # Write back to file
            self.LOG_FILE.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            print(f"Warning: Failed to write log: {e}")

    def exchange_code_for_token(self, auth_code: str) -> Dict:
        """
        Exchange authorization code for short-lived user access token

        Args:
            auth_code: Authorization code from OAuth callback

        Returns:
            Dict with access_token and token_type

        Raises:
            InstagramAuthError: On authentication failure
        """
        url = f"{self.GRAPH_API_BASE}/oauth/access_token"
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": self.redirect_uri,
            "code": auth_code
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                self._log_operation(
                    "exchange_code_for_token",
                    {"auth_code": auth_code[:10] + "..."},
                    {"status_code": 200, "has_token": "access_token" in response_data},
                    "success"
                )
                return {
                    "success": True,
                    "access_token": response_data.get("access_token"),
                    "token_type": response_data.get("token_type", "bearer")
                }
            else:
                error_type = response_data.get("error", {}).get("type", "unknown_error")
                error_message = response_data.get("error", {}).get("message", "Token exchange failed")

                self._log_operation(
                    "exchange_code_for_token",
                    {"auth_code": auth_code[:10] + "..."},
                    response_data,
                    "error"
                )

                raise InstagramAuthError(error_type, error_message, response_data)

        except requests.RequestException as e:
            self._log_operation(
                "exchange_code_for_token",
                {"auth_code": auth_code[:10] + "..."},
                {"error": str(e)},
                "error"
            )
            raise InstagramAuthError("network_error", f"Network request failed: {e}")

    def exchange_for_long_lived_token(self, short_lived_token: str) -> Dict:
        """
        Exchange short-lived token for long-lived token (60 days)

        Args:
            short_lived_token: Short-lived user access token

        Returns:
            Dict with access_token, token_type, and expires_in

        Raises:
            InstagramAuthError: On token exchange failure
        """
        url = f"{self.GRAPH_API_BASE}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_lived_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                expires_in = response_data.get("expires_in", 5184000)  # Default 60 days
                expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat() + "Z"

                self._log_operation(
                    "exchange_for_long_lived_token",
                    {"token": short_lived_token[:10] + "..."},
                    {"status_code": 200, "expires_in": expires_in},
                    "success"
                )

                return {
                    "success": True,
                    "access_token": response_data.get("access_token"),
                    "token_type": response_data.get("token_type", "bearer"),
                    "expires_in": expires_in,
                    "expires_at": expires_at
                }
            else:
                error_type = response_data.get("error", {}).get("type", "token_expired")
                error_message = response_data.get("error", {}).get("message", "Token exchange failed")

                self._log_operation(
                    "exchange_for_long_lived_token",
                    {"token": short_lived_token[:10] + "..."},
                    response_data,
                    "error"
                )

                raise InstagramAuthError(error_type, error_message, response_data)

        except requests.RequestException as e:
            self._log_operation(
                "exchange_for_long_lived_token",
                {"token": short_lived_token[:10] + "..."},
                {"error": str(e)},
                "error"
            )
            raise InstagramAuthError("network_error", f"Network request failed: {e}")

    def get_page_access_token(self, user_access_token: str) -> Dict:
        """
        Fetch Page Access Token and Instagram Business Account ID

        Args:
            user_access_token: Long-lived user access token

        Returns:
            Dict with page_access_token, page_id, instagram_business_account

        Raises:
            InstagramAuthError: On API failure
        """
        url = f"{self.GRAPH_API_BASE}/me/accounts"
        params = {
            "access_token": user_access_token,
            "fields": "access_token,id,instagram_business_account"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                pages = response_data.get("data", [])

                if not pages:
                    raise InstagramAuthError(
                        "permission_denied",
                        "No Facebook Pages found. User must have a Facebook Page connected to Instagram Business."
                    )

                # Get first page with Instagram Business Account
                page_with_ig = None
                for page in pages:
                    if "instagram_business_account" in page:
                        page_with_ig = page
                        break

                if not page_with_ig:
                    raise InstagramAuthError(
                        "invalid_scope",
                        "No Instagram Business Account found. Connect Instagram Business to Facebook Page."
                    )

                result = {
                    "success": True,
                    "page_access_token": page_with_ig.get("access_token"),
                    "page_id": page_with_ig.get("id"),
                    "instagram_business_account": page_with_ig.get("instagram_business_account", {}).get("id")
                }

                self._log_operation(
                    "get_page_access_token",
                    {"user_token": user_access_token[:10] + "..."},
                    {"status_code": 200, "has_ig_account": bool(result["instagram_business_account"])},
                    "success"
                )

                return result
            else:
                error_type = response_data.get("error", {}).get("type", "permission_denied")
                error_message = response_data.get("error", {}).get("message", "Failed to fetch page access token")

                self._log_operation(
                    "get_page_access_token",
                    {"user_token": user_access_token[:10] + "..."},
                    response_data,
                    "error"
                )

                raise InstagramAuthError(error_type, error_message, response_data)

        except requests.RequestException as e:
            self._log_operation(
                "get_page_access_token",
                {"user_token": user_access_token[:10] + "..."},
                {"error": str(e)},
                "error"
            )
            raise InstagramAuthError("network_error", f"Network request failed: {e}")

    def refresh_long_lived_token(self, current_token: str) -> Dict:
        """
        Refresh a long-lived token before it expires

        Args:
            current_token: Current long-lived access token

        Returns:
            Dict with new access_token and expires_at

        Raises:
            InstagramAuthError: On refresh failure
        """
        url = f"{self.GRAPH_API_BASE}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": current_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                expires_in = response_data.get("expires_in", 5184000)
                expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat() + "Z"

                self._log_operation(
                    "refresh_long_lived_token",
                    {"token": current_token[:10] + "..."},
                    {"status_code": 200, "expires_in": expires_in},
                    "success"
                )

                return {
                    "success": True,
                    "access_token": response_data.get("access_token"),
                    "expires_in": expires_in,
                    "expires_at": expires_at
                }
            else:
                error_type = response_data.get("error", {}).get("type", "token_expired")
                error_message = response_data.get("error", {}).get("message", "Token refresh failed")

                self._log_operation(
                    "refresh_long_lived_token",
                    {"token": current_token[:10] + "..."},
                    response_data,
                    "error"
                )

                raise InstagramAuthError(error_type, error_message, response_data)

        except requests.RequestException as e:
            self._log_operation(
                "refresh_long_lived_token",
                {"token": current_token[:10] + "..."},
                {"error": str(e)},
                "error"
            )
            raise InstagramAuthError("network_error", f"Network request failed: {e}")

    @staticmethod
    def is_token_expired(expires_at: str, buffer_days: int = 7) -> bool:
        """
        Check if token is expired or will expire soon

        Args:
            expires_at: ISO format expiration timestamp (with or without time/timezone)
            buffer_days: Days before expiration to consider token expired

        Returns:
            True if token is expired or will expire within buffer_days
        """
        try:
            # Parse the expiration date
            expiry_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

            # If the parsed date is naive (no timezone), assume UTC
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)

            # Get current time with timezone
            buffer_date = datetime.now(timezone.utc) + timedelta(days=buffer_days)

            return expiry_date <= buffer_date
        except (ValueError, AttributeError):
            return True  # Treat invalid dates as expired

    def complete_auth_flow(self, auth_code: str) -> Dict:
        """
        Complete full authentication flow from authorization code to credentials

        Args:
            auth_code: Authorization code from OAuth callback

        Returns:
            Dict with all credentials ready for storage

        Raises:
            InstagramAuthError: On any step failure
        """
        # Step 1: Exchange code for short-lived token
        short_token_result = self.exchange_code_for_token(auth_code)
        short_token = short_token_result["access_token"]

        # Step 2: Exchange for long-lived token
        long_token_result = self.exchange_for_long_lived_token(short_token)
        long_token = long_token_result["access_token"]
        expires_at = long_token_result["expires_at"]

        # Step 3: Get Page Access Token and Instagram Business Account
        page_result = self.get_page_access_token(long_token)

        return {
            "success": True,
            "credentials": {
                "IG_BUSINESS_ID": page_result["instagram_business_account"],
                "IG_PAGE_ACCESS_TOKEN": page_result["page_access_token"],
                "IG_TOKEN_EXPIRES_AT": expires_at,
                "FB_PAGE_ID": page_result["page_id"]
            }
        }


def save_credentials_to_env(credentials: Dict, env_file: str = ".env") -> bool:
    """
    Save credentials to .env file

    Args:
        credentials: Dict with credential key-value pairs
        env_file: Path to .env file

    Returns:
        True if successful
    """
    try:
        env_path = Path(env_file)

        # Read existing .env content
        if env_path.exists():
            env_content = env_path.read_text()
        else:
            env_content = ""

        # Update or append credentials
        for key, value in credentials.items():
            pattern = f"{key}="
            if pattern in env_content:
                # Update existing
                lines = env_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith(pattern):
                        lines[i] = f"{key}={value}"
                env_content = "\n".join(lines)
            else:
                # Append new
                if not env_content.endswith("\n"):
                    env_content += "\n"
                env_content += f"{key}={value}\n"

        env_path.write_text(env_content)
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python instagram_auth.py <authorization_code>")
        sys.exit(1)

    # Load from environment
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", "https://localhost/")

    if not app_id or not app_secret:
        print("Error: FACEBOOK_APP_ID and FACEBOOK_APP_SECRET must be set")
        sys.exit(1)

    auth = InstagramAuth(app_id, app_secret, redirect_uri)

    try:
        result = auth.complete_auth_flow(sys.argv[1])
        print(json.dumps(result, indent=2))

        # Save to .env
        if save_credentials_to_env(result["credentials"]):
            print("\nCredentials saved to .env file")
    except InstagramAuthError as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)
