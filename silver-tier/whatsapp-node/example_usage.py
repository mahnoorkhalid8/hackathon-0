"""
Simple example of using WhatsAppSender to send messages.
"""

from whatsapp_sender import WhatsAppSender

# Initialize the sender
sender = WhatsAppSender()

# Example 1: Send a simple message
print("Example 1: Sending a simple message")
success = sender.send_message(
    recipient="923332455342",  # Replace with recipient's number
    message="Hello! This is a test message from Python."
)

if success:
    print("Message sent successfully!\n")
else:
    print("Failed to send message.\n")

# Example 2: Enable human-in-the-loop approval
print("Example 2: With human approval")
sender.set_human_in_the_loop(True)
sender.send_message(
    recipient="923332455342",
    message="This message requires approval before sending."
)

# Example 3: View message history
print("\nExample 3: View recent message history")
history = sender.get_message_history(limit=5)
for msg in history:
    status_emoji = "✅" if msg['status'] == 'success' else "❌"
    print(f"{status_emoji} [{msg['timestamp']}] To: {msg['recipient']} - {msg['status']}")

# Example 4: Get account info
print("\nExample 4: Account information")
info = sender.get_account_info()
print(f"Logged in as: {info.get('name')} ({info.get('number')})")
