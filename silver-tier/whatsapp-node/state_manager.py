"""
WhatsApp State Manager Module

This module provides thread-safe read/write operations for whatsapp_state.json
and handles session management, message tracking, and statistics.

Features:
- Thread-safe state file operations
- Session validation and tracking
- Message lifecycle management
- Statistics tracking
- Automatic timestamp updates
- Prevents re-authentication by managing session state
"""

import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum


class MessageStatus(Enum):
    """Message status enumeration."""
    INCOMING = "incoming"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    FAILED = "failed"


class StateManager:
    """
    Thread-safe state manager for WhatsApp automation system.

    Manages session state, message tracking, and statistics to ensure
    no re-authentication is needed unless session is invalid.
    """

    def __init__(self, state_file: str = "whatsapp_state.json"):
        """
        Initialize the state manager.

        Args:
            state_file: Path to the state JSON file
        """
        self.state_file = Path(state_file)
        self._lock = threading.Lock()

        # Ensure state file exists
        if not self.state_file.exists():
            self._initialize_state_file()

    def _initialize_state_file(self):
        """Initialize a new state file with default structure."""
        default_state = {
            "session": {
                "authenticated": False,
                "last_authenticated": None,
                "session_valid": False,
                "session_path": ".wwebjs_auth",
                "requires_qr": True,
                "last_validation": None,
                "validation_interval_minutes": 30
            },
            "account_info": {
                "number": None,
                "name": None,
                "platform": None,
                "last_updated": None
            },
            "api_endpoint": "http://localhost:3000/api/whatsapp",
            "human_in_the_loop": False,
            "watcher_config": {
                "poll_interval_seconds": 5,
                "auto_reply_enabled": True,
                "process_group_messages": False,
                "max_messages_per_poll": 10
            },
            "retry_config": {
                "max_retries": 3,
                "retry_delay_seconds": 2,
                "exponential_backoff": True
            },
            "messages": {
                "incoming": [],
                "pending_approval": [],
                "approved": [],
                "rejected": [],
                "sent": [],
                "failed": []
            },
            "message_log": [],
            "incoming_messages": [],
            "pending_replies": [],
            "generated_replies": [],
            "statistics": {
                "total_incoming": 0,
                "total_sent": 0,
                "total_failed": 0,
                "total_approved": 0,
                "total_rejected": 0,
                "last_message_received": None,
                "last_message_sent": None
            },
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }

        self._write_state(default_state)

    def _read_state(self) -> dict:
        """
        Read state from file (thread-safe).

        Returns:
            dict: Current state
        """
        with self._lock:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)

    def _write_state(self, state: dict):
        """
        Write state to file (thread-safe).

        Args:
            state: State dictionary to write
        """
        with self._lock:
            # Update metadata timestamp
            if "metadata" not in state:
                state["metadata"] = {}
            state["metadata"]["last_updated"] = datetime.now().isoformat()

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

    def _update_state(self, update_func):
        """
        Update state using a function (thread-safe).

        Args:
            update_func: Function that takes state dict and modifies it
        """
        state = self._read_state()
        update_func(state)
        self._write_state(state)

    # ==================== Session Management ====================

    def is_session_valid(self) -> bool:
        """
        Check if the current session is valid.

        Returns:
            bool: True if session is valid and authenticated
        """
        state = self._read_state()
        session = state.get("session", {})

        # Check if authenticated
        if not session.get("authenticated", False):
            return False

        # Check if session is marked as valid
        if not session.get("session_valid", False):
            return False

        # Check if validation is recent
        last_validation = session.get("last_validation")
        if last_validation:
            validation_time = datetime.fromisoformat(last_validation)
            interval_minutes = session.get("validation_interval_minutes", 30)

            if datetime.now() - validation_time > timedelta(minutes=interval_minutes):
                # Validation expired, need to recheck
                return False

        return True

    def update_session_status(self, authenticated: bool, account_info: Optional[Dict] = None):
        """
        Update session authentication status.

        Args:
            authenticated: Whether session is authenticated
            account_info: Optional account information (number, name, platform)
        """
        def update(state):
            if "session" not in state:
                state["session"] = {}

            state["session"]["authenticated"] = authenticated
            state["session"]["session_valid"] = authenticated
            state["session"]["requires_qr"] = not authenticated
            state["session"]["last_validation"] = datetime.now().isoformat()

            if authenticated:
                state["session"]["last_authenticated"] = datetime.now().isoformat()

            if account_info:
                state["account_info"] = {
                    **account_info,
                    "last_updated": datetime.now().isoformat()
                }

        self._update_state(update)

    def mark_session_invalid(self, reason: str = "Unknown"):
        """
        Mark session as invalid (requires re-authentication).

        Args:
            reason: Reason for invalidation
        """
        def update(state):
            if "session" not in state:
                state["session"] = {}

            state["session"]["session_valid"] = False
            state["session"]["requires_qr"] = True
            state["session"]["invalidation_reason"] = reason
            state["session"]["invalidated_at"] = datetime.now().isoformat()

        self._update_state(update)

    def requires_qr_scan(self) -> bool:
        """
        Check if QR scan is required.

        Returns:
            bool: True if QR scan is needed
        """
        state = self._read_state()
        return state.get("session", {}).get("requires_qr", True)

    def get_session_info(self) -> Dict:
        """
        Get current session information.

        Returns:
            dict: Session information
        """
        state = self._read_state()
        return state.get("session", {})

    # ==================== Message Management ====================

    def add_message(self, message_data: Dict, status: MessageStatus):
        """
        Add a message to the appropriate queue.

        Args:
            message_data: Message data dictionary
            status: Message status
        """
        def update(state):
            if "messages" not in state:
                state["messages"] = {}

            status_key = status.value
            if status_key not in state["messages"]:
                state["messages"][status_key] = []

            # Add timestamp if not present
            if "timestamp" not in message_data:
                message_data["timestamp"] = datetime.now().isoformat()

            state["messages"][status_key].append(message_data)

            # Update statistics
            if status == MessageStatus.INCOMING:
                state["statistics"]["total_incoming"] += 1
                state["statistics"]["last_message_received"] = datetime.now().isoformat()
            elif status == MessageStatus.SENT:
                state["statistics"]["total_sent"] += 1
                state["statistics"]["last_message_sent"] = datetime.now().isoformat()
            elif status == MessageStatus.FAILED:
                state["statistics"]["total_failed"] += 1
            elif status == MessageStatus.APPROVED:
                state["statistics"]["total_approved"] += 1
            elif status == MessageStatus.REJECTED:
                state["statistics"]["total_rejected"] += 1

            # Limit queue sizes (keep last 100 per queue)
            for key in state["messages"]:
                if len(state["messages"][key]) > 100:
                    state["messages"][key] = state["messages"][key][-100:]

        self._update_state(update)

    def get_messages(self, status: MessageStatus, limit: Optional[int] = None) -> List[Dict]:
        """
        Get messages by status.

        Args:
            status: Message status to filter by
            limit: Maximum number of messages to return

        Returns:
            list: List of messages
        """
        state = self._read_state()
        messages = state.get("messages", {}).get(status.value, [])

        if limit:
            return messages[-limit:]
        return messages

    def move_message(self, message_id: str, from_status: MessageStatus, to_status: MessageStatus) -> bool:
        """
        Move a message from one status to another.

        Args:
            message_id: ID of the message to move
            from_status: Current status
            to_status: Target status

        Returns:
            bool: True if message was moved, False if not found
        """
        moved = False

        def update(state):
            nonlocal moved

            if "messages" not in state:
                return

            from_key = from_status.value
            to_key = to_status.value

            if from_key not in state["messages"] or to_key not in state["messages"]:
                return

            # Find and remove message from source
            message = None
            for i, msg in enumerate(state["messages"][from_key]):
                if msg.get("id") == message_id:
                    message = state["messages"][from_key].pop(i)
                    break

            if message:
                # Update status and timestamp
                message["status"] = to_status.value
                message["status_updated_at"] = datetime.now().isoformat()

                # Add to destination
                state["messages"][to_key].append(message)
                moved = True

                # Update statistics
                if to_status == MessageStatus.SENT:
                    state["statistics"]["total_sent"] += 1
                    state["statistics"]["last_message_sent"] = datetime.now().isoformat()
                elif to_status == MessageStatus.FAILED:
                    state["statistics"]["total_failed"] += 1
                elif to_status == MessageStatus.APPROVED:
                    state["statistics"]["total_approved"] += 1
                elif to_status == MessageStatus.REJECTED:
                    state["statistics"]["total_rejected"] += 1

        self._update_state(update)
        return moved

    def clear_messages(self, status: MessageStatus):
        """
        Clear all messages with a specific status.

        Args:
            status: Status of messages to clear
        """
        def update(state):
            if "messages" in state:
                status_key = status.value
                if status_key in state["messages"]:
                    state["messages"][status_key] = []

        self._update_state(update)

    # ==================== Statistics ====================

    def get_statistics(self) -> Dict:
        """
        Get current statistics.

        Returns:
            dict: Statistics dictionary
        """
        state = self._read_state()
        return state.get("statistics", {})

    def reset_statistics(self):
        """Reset all statistics to zero."""
        def update(state):
            state["statistics"] = {
                "total_incoming": 0,
                "total_sent": 0,
                "total_failed": 0,
                "total_approved": 0,
                "total_rejected": 0,
                "last_message_received": None,
                "last_message_sent": None
            }

        self._update_state(update)

    # ==================== Configuration ====================

    def get_config(self, key: str) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (e.g., "human_in_the_loop", "watcher_config")

        Returns:
            Configuration value
        """
        state = self._read_state()
        return state.get(key)

    def set_config(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        def update(state):
            state[key] = value

        self._update_state(update)

    def update_config(self, updates: Dict):
        """
        Update multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        def update(state):
            for key, value in updates.items():
                state[key] = value

        self._update_state(update)

    # ==================== Utility Functions ====================

    def get_full_state(self) -> Dict:
        """
        Get the complete state.

        Returns:
            dict: Full state dictionary
        """
        return self._read_state()

    def export_state(self, output_file: str):
        """
        Export state to a different file.

        Args:
            output_file: Path to output file
        """
        state = self._read_state()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def backup_state(self) -> str:
        """
        Create a backup of the current state.

        Returns:
            str: Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"whatsapp_state_backup_{timestamp}.json"
        self.export_state(backup_file)
        return backup_file


def main():
    """
    Example usage and testing of StateManager.
    """
    print("Testing WhatsApp State Manager\n")

    # Initialize state manager
    manager = StateManager()

    # Test session management
    print("1. Session Management:")
    print(f"   Session valid: {manager.is_session_valid()}")
    print(f"   Requires QR: {manager.requires_qr_scan()}")

    # Update session
    manager.update_session_status(
        authenticated=True,
        account_info={
            "number": "923332455342",
            "name": "Mahnoor",
            "platform": "iphone"
        }
    )
    print(f"   [OK] Session updated")
    print(f"   Session valid: {manager.is_session_valid()}")
    print(f"   Requires QR: {manager.requires_qr_scan()}\n")

    # Test message management
    print("2. Message Management:")

    # Add incoming message
    manager.add_message(
        {
            "id": "msg123",
            "from": "1234567890@c.us",
            "body": "Hello!",
            "fromName": "Test User"
        },
        MessageStatus.INCOMING
    )
    print(f"   [OK] Added incoming message")

    # Move to pending approval
    manager.move_message("msg123", MessageStatus.INCOMING, MessageStatus.PENDING_APPROVAL)
    print(f"   [OK] Moved to pending approval")

    # Approve and send
    manager.move_message("msg123", MessageStatus.PENDING_APPROVAL, MessageStatus.APPROVED)
    manager.move_message("msg123", MessageStatus.APPROVED, MessageStatus.SENT)
    print(f"   [OK] Approved and sent\n")

    # Test statistics
    print("3. Statistics:")
    stats = manager.get_statistics()
    print(f"   Total incoming: {stats['total_incoming']}")
    print(f"   Total sent: {stats['total_sent']}")
    print(f"   Total approved: {stats['total_approved']}\n")

    # Test configuration
    print("4. Configuration:")
    print(f"   Human-in-the-loop: {manager.get_config('human_in_the_loop')}")
    manager.set_config('human_in_the_loop', True)
    print(f"   Updated to: {manager.get_config('human_in_the_loop')}\n")

    # Create backup
    print("5. Backup:")
    backup_file = manager.backup_state()
    print(f"   [OK] Backup created: {backup_file}\n")

    print("[OK] All tests completed!")


if __name__ == "__main__":
    main()
