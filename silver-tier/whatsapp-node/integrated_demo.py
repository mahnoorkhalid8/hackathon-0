"""
Complete WhatsApp Automation System - Integrated Example

This script demonstrates how all components work together:
- state_manager.py - Session and message tracking
- whatsapp_sender.py - Send messages
- whatsapp_assistant.py - AI response generation
- whatsapp_watcher.py - Message monitoring

Features:
- No QR scan needed (uses existing session)
- Complete message lifecycle tracking
- Session validation
- Statistics and monitoring
"""

import time
from datetime import datetime
from state_manager import StateManager, MessageStatus
from whatsapp_sender import WhatsAppSender
from whatsapp_assistant import WhatsAppAssistant


class IntegratedWhatsAppSystem:
    """
    Integrated WhatsApp automation system with complete state management.
    """

    def __init__(self):
        """Initialize all components."""
        print("Initializing WhatsApp Automation System...")

        self.state_manager = StateManager()
        self.sender = WhatsAppSender()
        self.assistant = WhatsAppAssistant()

        print("[OK] All components initialized\n")

    def validate_session(self) -> bool:
        """
        Validate WhatsApp session before operations.

        Returns:
            bool: True if session is valid, False otherwise
        """
        print("Validating session...")

        # Check state manager
        if not self.state_manager.is_session_valid():
            print("[ERROR] Session invalid in state manager")

            # Try to get account info from backend
            account_info = self.sender.get_account_info()

            if account_info and account_info.get('number'):
                # Backend is authenticated, update state
                print("[OK] Backend authenticated, updating state...")
                self.state_manager.update_session_status(
                    authenticated=True,
                    account_info=account_info
                )
                return True
            else:
                print("[ERROR] Backend not authenticated")
                print("Please restart Node.js server and ensure WhatsApp is authenticated")
                return False

        print("[OK] Session valid")
        return True

    def process_incoming_message(self, message_data: dict) -> bool:
        """
        Process a single incoming message through the complete pipeline.

        Args:
            message_data: Incoming message data

        Returns:
            bool: True if processed successfully
        """
        message_id = message_data.get('id')
        sender_name = message_data.get('fromName', 'Unknown')
        message_body = message_data.get('body', '')

        print(f"\n{'='*70}")
        print(f"Processing message from {sender_name}")
        print(f"Message: {message_body[:60]}...")
        print(f"{'='*70}\n")

        # Step 1: Track incoming message
        print("Step 1: Tracking incoming message...")
        self.state_manager.add_message(message_data, MessageStatus.INCOMING)
        print("[OK] Message tracked\n")

        # Step 2: Generate AI response
        print("Step 2: Generating AI response...")
        response = self.assistant.process_message(message_data)

        if not response:
            print("[SKIP] No response generated (filtered)\n")
            return True

        print(f"[OK] Response generated: {response['message'][:60]}...\n")

        # Step 3: Create reply data
        reply_data = {
            "id": f"reply_{message_id}",
            "recipient": response['recipient'],
            "body": response['message'],
            "original_message_id": message_id
        }

        # Step 4: Add to pending approval
        print("Step 3: Adding to pending approval...")
        self.state_manager.add_message(reply_data, MessageStatus.PENDING_APPROVAL)
        print("[OK] Added to pending approval\n")

        # Step 5: Check if human approval required
        human_approval = self.state_manager.get_config('human_in_the_loop')

        if human_approval:
            print("Step 4: Requesting human approval...")
            print(f"Original: {message_body}")
            print(f"Reply: {response['message']}")

            approval = input("\nApprove this reply? (yes/no): ").strip().lower()

            if approval not in ['yes', 'y']:
                print("[REJECTED] Reply rejected by user\n")
                self.state_manager.move_message(
                    reply_data['id'],
                    MessageStatus.PENDING_APPROVAL,
                    MessageStatus.REJECTED
                )
                return True

            print("[OK] Reply approved\n")

        # Step 6: Move to approved
        print("Step 5: Approving reply...")
        self.state_manager.move_message(
            reply_data['id'],
            MessageStatus.PENDING_APPROVAL,
            MessageStatus.APPROVED
        )
        print("[OK] Reply approved\n")

        # Step 7: Send message
        print("Step 6: Sending message...")
        success = self.sender.send_message(
            reply_data['recipient'],
            reply_data['body']
        )

        # Step 8: Update status
        if success:
            print("[OK] Message sent successfully\n")
            self.state_manager.move_message(
                reply_data['id'],
                MessageStatus.APPROVED,
                MessageStatus.SENT
            )
        else:
            print("[ERROR] Failed to send message\n")
            self.state_manager.move_message(
                reply_data['id'],
                MessageStatus.APPROVED,
                MessageStatus.FAILED
            )

        return success

    def show_statistics(self):
        """Display current system statistics."""
        stats = self.state_manager.get_statistics()

        print("\n" + "="*70)
        print("SYSTEM STATISTICS")
        print("="*70)
        print(f"Total Incoming:  {stats['total_incoming']}")
        print(f"Total Sent:      {stats['total_sent']}")
        print(f"Total Failed:    {stats['total_failed']}")
        print(f"Total Approved:  {stats['total_approved']}")
        print(f"Total Rejected:  {stats['total_rejected']}")

        if stats['total_incoming'] > 0:
            success_rate = (stats['total_sent'] / stats['total_incoming']) * 100
            print(f"Success Rate:    {success_rate:.1f}%")

        print(f"\nLast Message Received: {stats['last_message_received']}")
        print(f"Last Message Sent:     {stats['last_message_sent']}")
        print("="*70 + "\n")

    def show_session_info(self):
        """Display current session information."""
        session = self.state_manager.get_session_info()
        account = self.state_manager.get_config('account_info')

        print("\n" + "="*70)
        print("SESSION INFORMATION")
        print("="*70)
        print(f"Authenticated:   {session.get('authenticated')}")
        print(f"Session Valid:   {session.get('session_valid')}")
        print(f"Requires QR:     {session.get('requires_qr')}")
        print(f"Last Validated:  {session.get('last_validation')}")

        if account:
            print(f"\nAccount Number:  {account.get('number')}")
            print(f"Account Name:    {account.get('name')}")
            print(f"Platform:        {account.get('platform')}")

        print("="*70 + "\n")

    def run_demo(self):
        """Run a complete demonstration of the system."""
        print("\n" + "="*70)
        print("WHATSAPP AUTOMATION SYSTEM - INTEGRATED DEMO")
        print("="*70 + "\n")

        # Step 1: Validate session
        if not self.validate_session():
            print("\n[ERROR] Cannot proceed without valid session")
            return

        # Step 2: Show session info
        self.show_session_info()

        # Step 3: Simulate incoming message
        print("Simulating incoming message...\n")

        test_message = {
            "id": f"test_{int(time.time())}",
            "from": "923332455342@c.us",
            "fromName": "Test User",
            "body": "Hello! Can you help me with something?",
            "timestamp": int(time.time()),
            "isGroup": False,
            "type": "chat",
            "hasMedia": False,
            "receivedAt": datetime.now().isoformat()
        }

        # Step 4: Process message
        success = self.process_incoming_message(test_message)

        # Step 5: Show statistics
        self.show_statistics()

        # Step 6: Show message queues
        print("MESSAGE QUEUES:")
        print(f"  Incoming:         {len(self.state_manager.get_messages(MessageStatus.INCOMING))}")
        print(f"  Pending Approval: {len(self.state_manager.get_messages(MessageStatus.PENDING_APPROVAL))}")
        print(f"  Approved:         {len(self.state_manager.get_messages(MessageStatus.APPROVED))}")
        print(f"  Sent:             {len(self.state_manager.get_messages(MessageStatus.SENT))}")
        print(f"  Failed:           {len(self.state_manager.get_messages(MessageStatus.FAILED))}")
        print(f"  Rejected:         {len(self.state_manager.get_messages(MessageStatus.REJECTED))}")

        # Step 7: Create backup
        print("\nCreating state backup...")
        backup_file = self.state_manager.backup_state()
        print(f"[OK] Backup created: {backup_file}")

        print("\n" + "="*70)
        print("DEMO COMPLETED")
        print("="*70 + "\n")


def main():
    """Main entry point."""
    try:
        system = IntegratedWhatsAppSystem()
        system.run_demo()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
