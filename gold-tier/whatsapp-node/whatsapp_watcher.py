"""
WhatsApp Watcher Module

This module continuously monitors incoming WhatsApp messages and automatically
generates and sends AI-powered responses using the WhatsApp Assistant.

Features:
- Polls for new incoming messages from Node.js backend
- Processes messages through AI assistant
- Human-in-the-loop approval for replies (configurable)
- Stores all incoming messages and pending replies in state file
- Automatic retry logic and error handling
- No QR scan required (uses existing authenticated session)
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from whatsapp_assistant import WhatsAppAssistant
from whatsapp_sender import WhatsAppSender


class WhatsAppWatcher:
    """
    WhatsApp message watcher that monitors incoming messages and generates responses.

    Attributes:
        state_file (Path): Path to the state configuration file
        state (dict): Current state loaded from whatsapp_state.json
        api_endpoint (str): Base URL for the WhatsApp API
        assistant (WhatsAppAssistant): AI assistant for generating responses
        sender (WhatsAppSender): Message sender for sending replies
    """

    def __init__(self, state_file: str = "whatsapp_state.json"):
        """
        Initialize the WhatsApp watcher.

        Args:
            state_file: Path to the JSON state file (default: whatsapp_state.json)
        """
        self.state_file = Path(state_file)
        self.state = self._load_state()
        self.api_endpoint = self.state.get("api_endpoint", "http://localhost:3000/api/whatsapp")

        # Initialize assistant and sender
        self.assistant = WhatsAppAssistant(state_file)
        self.sender = WhatsAppSender(state_file)

        # Watcher state
        self.is_running = False
        self.processed_message_ids = set()

    def _load_state(self) -> dict:
        """
        Load state from whatsapp_state.json file.

        Returns:
            dict: State configuration

        Raises:
            FileNotFoundError: If state file doesn't exist
        """
        if not self.state_file.exists():
            raise FileNotFoundError(f"State file not found: {self.state_file}")

        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """Save current state back to whatsapp_state.json file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _reload_state(self):
        """Reload state from file to get latest configuration."""
        self.state = self._load_state()

    def _log_incoming_message(self, message_data: Dict):
        """
        Log incoming message to state file.

        Args:
            message_data: Dictionary containing message information
        """
        if "incoming_messages" not in self.state:
            self.state["incoming_messages"] = []

        log_entry = {
            "id": message_data.get('id'),
            "from": message_data.get('from'),
            "fromName": message_data.get('fromName'),
            "body": message_data.get('body'),
            "timestamp": message_data.get('timestamp'),
            "receivedAt": message_data.get('receivedAt'),
            "isGroup": message_data.get('isGroup'),
            "processed": True,
            "processedAt": datetime.now().isoformat()
        }

        self.state["incoming_messages"].append(log_entry)

        # Limit stored messages
        if len(self.state["incoming_messages"]) > 100:
            self.state["incoming_messages"] = self.state["incoming_messages"][-100:]

        self._save_state()

    def _log_pending_reply(self, reply_data: Dict, status: str = "pending"):
        """
        Log pending reply to state file.

        Args:
            reply_data: Dictionary containing reply information
            status: Status of the reply (pending/sent/rejected/failed)
        """
        if "pending_replies" not in self.state:
            self.state["pending_replies"] = []

        log_entry = {
            "recipient": reply_data.get('recipient'),
            "message": reply_data.get('message'),
            "original_message_id": reply_data.get('original_message_id'),
            "generated_at": reply_data.get('generated_at'),
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        self.state["pending_replies"].append(log_entry)

        # Limit stored replies
        if len(self.state["pending_replies"]) > 50:
            self.state["pending_replies"] = self.state["pending_replies"][-50:]

        self._save_state()

    def _update_reply_status(self, original_message_id: str, status: str):
        """
        Update status of a pending reply.

        Args:
            original_message_id: ID of the original message
            status: New status (sent/rejected/failed)
        """
        if "pending_replies" not in self.state:
            return

        for reply in self.state["pending_replies"]:
            if reply.get("original_message_id") == original_message_id:
                reply["status"] = status
                reply["updated_at"] = datetime.now().isoformat()

        self._save_state()

    def _fetch_incoming_messages(self) -> List[Dict]:
        """
        Fetch unprocessed incoming messages from the Node.js backend.

        Returns:
            list: List of unprocessed message dictionaries

        Raises:
            Exception: If API request fails
        """
        try:
            response = requests.get(
                f"{self.api_endpoint}/messages",
                params={"unprocessed": "true"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('messages', [])

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch messages: {e}")

    def _mark_message_processed(self, message_id: str) -> bool:
        """
        Mark a message as processed in the Node.js backend.

        Args:
            message_id: ID of the message to mark as processed

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_endpoint}/messages/{message_id}/processed",
                timeout=5
            )
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"⚠️  Failed to mark message as processed: {e}")
            return False

    def _request_human_approval(self, message_data: Dict, reply_data: Dict) -> bool:
        """
        Request human approval before sending reply.

        Args:
            message_data: Original incoming message data
            reply_data: Generated reply data

        Returns:
            bool: True if approved, False if rejected
        """
        print("\n" + "="*70)
        print("🔔 HUMAN APPROVAL REQUIRED FOR REPLY")
        print("="*70)
        print(f"From: {message_data.get('fromName')} ({message_data.get('from')})")
        print(f"Incoming Message: {message_data.get('body')}")
        print("-"*70)
        print(f"Proposed Reply: {reply_data.get('message')}")
        print("="*70)

        while True:
            approval = input("Send this reply? (yes/no/edit): ").strip().lower()

            if approval in ['yes', 'y']:
                return True
            elif approval in ['no', 'n']:
                return False
            elif approval in ['edit', 'e']:
                new_message = input("Enter new reply message: ").strip()
                if new_message:
                    reply_data['message'] = new_message
                    print(f"✏️  Reply updated to: {new_message}")
                    return True
            else:
                print("Please enter 'yes', 'no', or 'edit'")

    def process_message(self, message_data: Dict) -> bool:
        """
        Process a single incoming message and send reply if appropriate.

        Args:
            message_data: Dictionary containing message information

        Returns:
            bool: True if processed successfully, False otherwise
        """
        message_id = message_data.get('id')
        sender_name = message_data.get('fromName', 'Unknown')
        message_body = message_data.get('body', '')

        print(f"\n📨 Processing message from {sender_name}: {message_body[:60]}...")

        # Skip if already processed
        if message_id in self.processed_message_ids:
            print(f"⏭️  Already processed, skipping")
            return True

        # Log incoming message
        self._log_incoming_message(message_data)

        # Generate response using AI assistant
        reply_data = self.assistant.process_message(message_data)

        if not reply_data:
            print(f"⏭️  No response generated (filtered or skipped)")
            self.processed_message_ids.add(message_id)
            self._mark_message_processed(message_id)
            return True

        # Log pending reply
        self._log_pending_reply(reply_data, status="pending")

        # Check human-in-the-loop approval
        if self.state.get("human_in_the_loop", False):
            if not self._request_human_approval(message_data, reply_data):
                print("🚫 Reply rejected by user")
                self._update_reply_status(message_id, "rejected")
                self.processed_message_ids.add(message_id)
                self._mark_message_processed(message_id)
                return True

        # Send reply
        print(f"📤 Sending reply to {reply_data['recipient']}...")
        success = self.sender.send_message(
            recipient=reply_data['recipient'],
            message=reply_data['message']
        )

        if success:
            print(f"✅ Reply sent successfully!")
            self._update_reply_status(message_id, "sent")
        else:
            print(f"❌ Failed to send reply")
            self._update_reply_status(message_id, "failed")

        # Mark as processed
        self.processed_message_ids.add(message_id)
        self._mark_message_processed(message_id)

        return success

    def run_once(self) -> int:
        """
        Run one iteration of the watcher (fetch and process messages).

        Returns:
            int: Number of messages processed
        """
        try:
            # Fetch unprocessed messages
            messages = self._fetch_incoming_messages()

            if not messages:
                return 0

            print(f"\n📬 Found {len(messages)} unprocessed message(s)")

            # Process each message
            processed_count = 0
            for message in messages:
                try:
                    if self.process_message(message):
                        processed_count += 1
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue

            return processed_count

        except Exception as e:
            print(f"❌ Error in watcher iteration: {e}")
            return 0

    def start(self, poll_interval: Optional[int] = None):
        """
        Start the watcher in continuous monitoring mode.

        Args:
            poll_interval: Seconds between polls (default from config)
        """
        if poll_interval is None:
            poll_interval = self.state.get('watcher_config', {}).get('poll_interval_seconds', 5)

        self.is_running = True
        print("="*70)
        print("🚀 WhatsApp Watcher Started")
        print("="*70)
        print(f"Poll Interval: {poll_interval} seconds")
        print(f"Human-in-the-loop: {'Enabled' if self.state.get('human_in_the_loop') else 'Disabled'}")
        print(f"Auto-reply: {'Enabled' if self.state.get('watcher_config', {}).get('auto_reply_enabled') else 'Disabled'}")
        print("="*70)
        print("Press Ctrl+C to stop\n")

        try:
            while self.is_running:
                # Reload state to get latest configuration
                self._reload_state()

                # Check if auto-reply is enabled
                if not self.state.get('watcher_config', {}).get('auto_reply_enabled', True):
                    print("⏸️  Auto-reply disabled, waiting...")
                    time.sleep(poll_interval)
                    continue

                # Run one iteration
                processed = self.run_once()

                if processed > 0:
                    print(f"✅ Processed {processed} message(s)")

                # Wait before next poll
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Watcher stopped by user")
            self.is_running = False

        except Exception as e:
            print(f"\n\n❌ Watcher stopped due to error: {e}")
            self.is_running = False

    def stop(self):
        """Stop the watcher."""
        self.is_running = False
        print("🛑 Stopping watcher...")


def main():
    """
    Main entry point for the WhatsApp watcher.
    """
    print("🤖 WhatsApp Watcher - AI-Powered Message Responder\n")

    try:
        watcher = WhatsAppWatcher()

        # Start watching
        watcher.start()

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure whatsapp_state.json exists and the Node.js server is running.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
