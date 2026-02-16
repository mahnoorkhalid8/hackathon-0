"""
WhatsApp AI Assistant Module - Claude API Integration

This module generates AI-powered responses to incoming WhatsApp messages using
Anthropic's Claude API.

Features:
- Generate contextual responses using Claude AI
- Maintain conversation history per contact
- Log all generated replies for approval
- Customizable AI personality and behavior
- Robust error handling and fallback responses
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path
from anthropic import Anthropic, APIError, APIConnectionError


class WhatsAppAssistant:
    """
    AI Assistant for generating WhatsApp message responses using Claude API.

    This assistant uses Anthropic's Claude to generate intelligent, contextual
    responses to incoming WhatsApp messages.
    """

    def __init__(self, state_file: str = "whatsapp_state.json"):
        """
        Initialize the AI assistant with Claude API.

        Args:
            state_file: Path to the state configuration file

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set
        """
        self.state_file = Path(state_file)
        self.state = self._load_state()

        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_api_key_here':
            print("⚠️  WARNING: ANTHROPIC_API_KEY not set. Using fallback responses.")
            print("   Set your API key in .env file to enable Claude AI.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

        # Assistant configuration
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.max_tokens = 500
        self.temperature = 0.7

        # Personality and behavior
        self.system_prompt = """You are a helpful WhatsApp assistant. Your responses should be:
- Friendly and conversational
- Concise (2-3 sentences max for simple queries)
- Clear and easy to understand
- Appropriate for WhatsApp messaging (casual but professional)
- Helpful and informative

Keep responses brief unless the user asks for detailed information."""

        # Conversation history (in-memory)
        self.conversation_history = {}
        self.max_history_per_contact = 10

    def _load_state(self) -> dict:
        """Load state from whatsapp_state.json file."""
        if not self.state_file.exists():
            raise FileNotFoundError(f"State file not found: {self.state_file}")

        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """Save current state back to whatsapp_state.json file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _get_conversation_context(self, sender: str, limit: int = 5) -> List[Dict]:
        """
        Get recent conversation history with a specific sender.

        Args:
            sender: Phone number of the sender
            limit: Maximum number of messages to retrieve

        Returns:
            list: Recent messages in conversation
        """
        if sender not in self.conversation_history:
            self.conversation_history[sender] = []

        return self.conversation_history[sender][-limit:]

    def _update_conversation_history(self, sender: str, message: str, is_incoming: bool):
        """
        Update conversation history with new message.

        Args:
            sender: Phone number of the sender
            message: Message content
            is_incoming: True if incoming message, False if outgoing
        """
        if sender not in self.conversation_history:
            self.conversation_history[sender] = []

        self.conversation_history[sender].append({
            "message": message,
            "is_incoming": is_incoming,
            "timestamp": datetime.now().isoformat()
        })

        # Limit history size
        if len(self.conversation_history[sender]) > self.max_history_per_contact:
            self.conversation_history[sender] = self.conversation_history[sender][-self.max_history_per_contact:]

    def _log_generated_reply(self, message_data: Dict, generated_reply: str, status: str = "pending_approval"):
        """
        Log generated reply to state file for approval tracking.

        Args:
            message_data: Original message data
            generated_reply: AI-generated response
            status: Status of the reply (pending_approval/approved/rejected)
        """
        if "generated_replies" not in self.state:
            self.state["generated_replies"] = []

        log_entry = {
            "id": f"reply_{datetime.now().timestamp()}",
            "original_message_id": message_data.get('id'),
            "from": message_data.get('from'),
            "fromName": message_data.get('fromName'),
            "original_message": message_data.get('body'),
            "generated_reply": generated_reply,
            "status": status,
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        }

        self.state["generated_replies"].append(log_entry)

        # Limit stored replies
        if len(self.state["generated_replies"]) > 100:
            self.state["generated_replies"] = self.state["generated_replies"][-100:]

        self._save_state()

    def _generate_claude_response(self, message: str, sender_name: str, context: List[Dict]) -> str:
        """
        Generate response using Claude API.

        Args:
            message: Incoming message text
            sender_name: Name of the sender
            context: Recent conversation history

        Returns:
            str: Generated response

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            return self._generate_fallback_response(message, sender_name)

        try:
            # Build conversation messages for Claude
            messages = []

            # Add conversation context
            for msg in context:
                role = "user" if msg['is_incoming'] else "assistant"
                messages.append({
                    "role": role,
                    "content": msg['message']
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages
            )

            # Extract response text
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                return self._generate_fallback_response(message, sender_name)

        except APIConnectionError as e:
            print(f"❌ Claude API connection error: {e}")
            return self._generate_fallback_response(message, sender_name)

        except APIError as e:
            print(f"❌ Claude API error: {e}")
            return self._generate_fallback_response(message, sender_name)

        except Exception as e:
            print(f"❌ Unexpected error calling Claude: {e}")
            return self._generate_fallback_response(message, sender_name)

    def _generate_fallback_response(self, message: str, sender_name: str) -> str:
        """
        Generate a simple fallback response when Claude API is unavailable.

        Args:
            message: Incoming message text
            sender_name: Name of the sender

        Returns:
            str: Fallback response
        """
        message_lower = message.lower()

        # Simple keyword-based responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'salam']):
            return f"Hello {sender_name}! How can I help you today?"

        elif any(word in message_lower for word in ['how are you', 'how r u', 'kaise ho']):
            return "I'm doing great, thank you for asking! How can I assist you?"

        elif any(word in message_lower for word in ['thanks', 'thank you', 'shukriya']):
            return "You're welcome! Let me know if you need anything else."

        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Feel free to message me anytime."

        elif '?' in message:
            return f"That's an interesting question! I'm currently running in fallback mode. Please set up the Claude API key for intelligent responses."

        else:
            return f"Thanks for your message! I received it but I'm running in fallback mode. Please configure the Claude API key for AI-powered responses."

    def generate_response(self, message_data: Dict) -> Optional[str]:
        """
        Generate an AI response to an incoming message using Claude.

        Args:
            message_data: Dictionary containing message information
                - from: sender phone number
                - fromName: sender name
                - body: message content
                - timestamp: message timestamp

        Returns:
            str: Generated response, or None if no response should be sent
        """
        sender = message_data.get('from')
        sender_name = message_data.get('fromName', 'User')
        message_body = message_data.get('body', '').strip()

        # Skip empty messages
        if not message_body:
            return None

        # Get conversation context
        context = self._get_conversation_context(sender)

        # Update history with incoming message
        self._update_conversation_history(sender, message_body, is_incoming=True)

        print(f"🤖 Generating Claude response for: {message_body[:50]}...")

        # Generate response using Claude
        try:
            response = self._generate_claude_response(message_body, sender_name, context)

            # Log generated reply for approval tracking
            self._log_generated_reply(message_data, response, status="pending_approval")

            # Update history with outgoing response
            self._update_conversation_history(sender, response, is_incoming=False)

            return response

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None

    def should_respond(self, message_data: Dict) -> bool:
        """
        Determine if the assistant should respond to this message.

        Args:
            message_data: Dictionary containing message information

        Returns:
            bool: True if should respond, False otherwise
        """
        # Don't respond to group messages (configurable)
        if message_data.get('isGroup') and not self.state.get('watcher_config', {}).get('process_group_messages', False):
            return False

        # Don't respond to empty messages
        if not message_data.get('body', '').strip():
            return False

        # Don't respond to media-only messages (for now)
        if message_data.get('hasMedia') and not message_data.get('body'):
            return False

        return True

    def process_message(self, message_data: Dict) -> Optional[Dict]:
        """
        Process an incoming message and generate a response.

        This is the main entry point called by whatsapp_watcher.py.

        Args:
            message_data: Dictionary containing message information

        Returns:
            dict: Response data with recipient and message, or None if no response
                {
                    "recipient": "phone_number",
                    "message": "response_text",
                    "original_message_id": "msg_id",
                    "generated_at": "timestamp"
                }
        """
        # Check if we should respond
        if not self.should_respond(message_data):
            print(f"⏭️  Skipping message from {message_data.get('fromName')} (filtered)")
            return None

        print(f"🤖 Processing message from {message_data.get('fromName')}: {message_data.get('body')[:50]}...")

        # Generate response
        response_text = self.generate_response(message_data)

        if not response_text:
            return None

        # Extract phone number from 'from' field (format: 1234567890@c.us)
        sender = message_data.get('from', '')
        phone_number = sender.split('@')[0] if '@' in sender else sender

        return {
            "recipient": phone_number,
            "message": response_text,
            "original_message_id": message_data.get('id'),
            "generated_at": datetime.now().isoformat()
        }

    def get_generated_replies(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get generated replies from state file.

        Args:
            status: Filter by status (pending_approval/approved/rejected), None for all

        Returns:
            list: List of generated reply entries
        """
        replies = self.state.get("generated_replies", [])

        if status:
            return [r for r in replies if r.get("status") == status]

        return replies

    def update_reply_status(self, reply_id: str, status: str) -> bool:
        """
        Update the status of a generated reply.

        Args:
            reply_id: ID of the reply to update
            status: New status (approved/rejected)

        Returns:
            bool: True if updated, False if not found
        """
        if "generated_replies" not in self.state:
            return False

        for reply in self.state["generated_replies"]:
            if reply.get("id") == reply_id:
                reply["status"] = status
                reply["updated_at"] = datetime.now().isoformat()
                self._save_state()
                return True

        return False


def main():
    """
    Example usage and testing of WhatsAppAssistant with Claude API.
    """
    print("🤖 Testing WhatsApp Assistant with Claude API\n")

    # Check if API key is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your_anthropic_api_key_here':
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("   Set it in .env file to enable Claude AI.\n")

    assistant = WhatsAppAssistant()

    # Example message data
    test_message = {
        "id": "test123",
        "from": "923332455342@c.us",
        "fromName": "Test User",
        "body": "Hello! Can you help me understand how AI works?",
        "timestamp": 1234567890,
        "isGroup": False,
        "type": "chat",
        "hasMedia": False
    }

    print(f"Incoming: {test_message['body']}\n")

    response = assistant.process_message(test_message)

    if response:
        print(f"✅ Response generated:")
        print(f"   To: {response['recipient']}")
        print(f"   Message: {response['message']}\n")

        # Show generated replies log
        print("📋 Generated replies log:")
        replies = assistant.get_generated_replies(status="pending_approval")
        for reply in replies[-3:]:
            print(f"   • {reply.get('fromName')}: {reply.get('generated_reply')[:60]}...")
    else:
        print("❌ No response generated")


if __name__ == "__main__":
    main()
