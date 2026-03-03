"""
WhatsApp Sender Module

This module provides a Python interface to send WhatsApp messages using an already
authenticated WhatsApp session via the Node.js backend service.

Features:
- Uses saved session state (whatsapp_state.json)
- Human-in-the-loop approval before sending (configurable)
- Message logging with timestamps
- Automatic retry logic with exponential backoff
- Error handling and validation
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class WhatsAppSender:
    """
    WhatsApp message sender that interfaces with the Node.js backend.

    Attributes:
        state_file (Path): Path to the state configuration file
        state (dict): Current state loaded from whatsapp_state.json
        api_endpoint (str): Base URL for the WhatsApp API
    """

    def __init__(self, state_file: str = "whatsapp_state.json"):
        """
        Initialize the WhatsApp sender with state file.

        Args:
            state_file: Path to the JSON state file (default: whatsapp_state.json)
        """
        self.state_file = Path(state_file)
        self.state = self._load_state()
        self.api_endpoint = self.state.get("api_endpoint", "http://localhost:3000/api/whatsapp")

    def _load_state(self) -> dict:
        """
        Load state from whatsapp_state.json file.

        Returns:
            dict: State configuration

        Raises:
            FileNotFoundError: If state file doesn't exist
            json.JSONDecodeError: If state file is invalid JSON
        """
        if not self.state_file.exists():
            raise FileNotFoundError(f"State file not found: {self.state_file}")

        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """Save current state back to whatsapp_state.json file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _check_authentication(self) -> bool:
        """
        Check if WhatsApp session is authenticated and ready.

        Returns:
            bool: True if authenticated and ready, False otherwise
        """
        try:
            response = requests.get(f"{self.api_endpoint}/status", timeout=5)
            response.raise_for_status()
            status = response.json()
            return status.get("isReady", False)
        except requests.RequestException as e:
            print(f"❌ Error checking authentication: {e}")
            return False

    def _request_human_approval(self, recipient: str, message: str) -> bool:
        """
        Request human approval before sending message.

        Args:
            recipient: Phone number of recipient
            message: Message content to be sent

        Returns:
            bool: True if approved, False if rejected
        """
        print("\n" + "="*60)
        print("🔔 HUMAN APPROVAL REQUIRED")
        print("="*60)
        print(f"Recipient: {recipient}")
        print(f"Message: {message}")
        print("="*60)

        while True:
            approval = input("Send this message? (yes/no): ").strip().lower()
            if approval in ['yes', 'y']:
                return True
            elif approval in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")

    def _log_message(self, recipient: str, message: str, status: str,
                     message_id: Optional[str] = None, error: Optional[str] = None):
        """
        Log sent message to state file.

        Args:
            recipient: Phone number of recipient
            message: Message content
            status: Status of message (success/failed/rejected)
            message_id: WhatsApp message ID (if successful)
            error: Error message (if failed)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "recipient": recipient,
            "message": message,
            "status": status,
            "message_id": message_id,
            "error": error
        }

        if "message_log" not in self.state:
            self.state["message_log"] = []

        self.state["message_log"].append(log_entry)
        self._save_state()

    def _send_with_retry(self, recipient: str, message: str) -> Dict:
        """
        Send message with retry logic and exponential backoff.

        Args:
            recipient: Phone number of recipient
            message: Message content

        Returns:
            dict: Response from API with success status

        Raises:
            Exception: If all retry attempts fail
        """
        max_retries = self.state.get("retry_config", {}).get("max_retries", 3)
        retry_delay = self.state.get("retry_config", {}).get("retry_delay_seconds", 2)

        last_error = None

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.api_endpoint}/send",
                    json={"number": recipient, "message": message},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ All {max_retries} attempts failed")

        raise Exception(f"Failed to send message after {max_retries} attempts: {last_error}")

    def send_message(self, recipient: str, message: str) -> bool:
        """
        Send a WhatsApp message to the specified recipient.

        This is the main public method to send messages. It handles:
        - Authentication check
        - Human-in-the-loop approval (if enabled)
        - Message sending with retry logic
        - Logging of all attempts

        Args:
            recipient: Phone number with country code (e.g., "923332455342")
            message: Text message to send

        Returns:
            bool: True if message sent successfully, False otherwise

        Example:
            >>> sender = WhatsAppSender()
            >>> sender.send_message("923332455342", "Hello from Python!")
            ✅ Message sent successfully!
            True
        """
        # Validate inputs
        if not recipient or not message:
            print("❌ Error: Recipient and message are required")
            return False

        # Check authentication status
        if not self._check_authentication():
            print("❌ Error: WhatsApp is not authenticated. Please authenticate first.")
            self._log_message(recipient, message, "failed", error="Not authenticated")
            return False

        # Check human-in-the-loop flag
        if self.state.get("human_in_the_loop", False):
            if not self._request_human_approval(recipient, message):
                print("🚫 Message sending cancelled by user")
                self._log_message(recipient, message, "rejected")
                return False

        # Send message with retry logic
        try:
            print(f"📤 Sending message to {recipient}...")
            result = self._send_with_retry(recipient, message)

            if result.get("success"):
                message_id = result.get("messageId")
                print(f"✅ Message sent successfully! (ID: {message_id})")
                self._log_message(recipient, message, "success", message_id=message_id)
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"❌ Failed to send message: {error_msg}")
                self._log_message(recipient, message, "failed", error=error_msg)
                return False

        except Exception as e:
            print(f"❌ Error sending message: {e}")
            self._log_message(recipient, message, "failed", error=str(e))
            return False

    def get_message_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get message history from state file.

        Args:
            limit: Maximum number of messages to return (None for all)

        Returns:
            list: List of message log entries
        """
        messages = self.state.get("message_log", [])
        if limit:
            return messages[-limit:]
        return messages

    def get_account_info(self) -> Dict:
        """
        Get authenticated WhatsApp account information.

        Returns:
            dict: Account information (number, name, platform)
        """
        try:
            response = requests.get(f"{self.api_endpoint}/info", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error getting account info: {e}")
            return {}

    def set_human_in_the_loop(self, enabled: bool):
        """
        Enable or disable human-in-the-loop approval.

        Args:
            enabled: True to require approval, False to send automatically
        """
        self.state["human_in_the_loop"] = enabled
        self._save_state()
        status = "enabled" if enabled else "disabled"
        print(f"✅ Human-in-the-loop {status}")


def main():
    """
    Example usage and testing of WhatsAppSender.
    """
    # Initialize sender
    sender = WhatsAppSender()

    # Get account info
    print("📱 WhatsApp Account Info:")
    info = sender.get_account_info()
    print(f"   Number: {info.get('number')}")
    print(f"   Name: {info.get('name')}")
    print(f"   Platform: {info.get('platform')}")
    print()

    # Example: Send a test message
    test_recipient = "923332455342"  # Replace with actual number
    test_message = "🤖 Test message from Python WhatsApp Sender!"

    success = sender.send_message(test_recipient, test_message)

    if success:
        print("\n📊 Recent message history:")
        history = sender.get_message_history(limit=5)
        for entry in history:
            print(f"   [{entry['timestamp']}] {entry['recipient']}: {entry['status']}")


if __name__ == "__main__":
    main()
