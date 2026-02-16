"""
Quick Start Guide for WhatsApp Watcher System

This script demonstrates how to use the complete WhatsApp automation system.
"""

from whatsapp_watcher import WhatsAppWatcher
from whatsapp_assistant import WhatsAppAssistant
from whatsapp_sender import WhatsAppSender
import json


def test_components():
    """Test individual components."""
    print("="*70)
    print("🧪 Testing WhatsApp Components")
    print("="*70)

    # Test 1: Sender
    print("\n1️⃣ Testing WhatsApp Sender...")
    sender = WhatsAppSender()
    info = sender.get_account_info()
    print(f"   ✅ Connected as: {info.get('name')} ({info.get('number')})")

    # Test 2: Assistant
    print("\n2️⃣ Testing AI Assistant...")
    assistant = WhatsAppAssistant()
    test_message = {
        "id": "test123",
        "from": "923332455342@c.us",
        "fromName": "Test User",
        "body": "Hello!",
        "timestamp": 1234567890,
        "isGroup": False,
        "type": "chat",
        "hasMedia": False
    }
    response = assistant.process_message(test_message)
    if response:
        print(f"   ✅ Generated response: {response['message'][:50]}...")
    else:
        print(f"   ⚠️  No response generated")

    # Test 3: Watcher
    print("\n3️⃣ Testing Watcher (single iteration)...")
    watcher = WhatsAppWatcher()
    processed = watcher.run_once()
    print(f"   ✅ Processed {processed} message(s)")

    print("\n" + "="*70)
    print("✅ All components tested successfully!")
    print("="*70)


def configure_watcher():
    """Interactive configuration for the watcher."""
    print("\n" + "="*70)
    print("⚙️  WhatsApp Watcher Configuration")
    print("="*70)

    with open('whatsapp_state.json', 'r') as f:
        state = json.load(f)

    print("\nCurrent Configuration:")
    print(f"  • Human-in-the-loop: {state.get('human_in_the_loop')}")
    print(f"  • Auto-reply enabled: {state.get('watcher_config', {}).get('auto_reply_enabled')}")
    print(f"  • Poll interval: {state.get('watcher_config', {}).get('poll_interval_seconds')}s")
    print(f"  • Process group messages: {state.get('watcher_config', {}).get('process_group_messages')}")

    print("\nWould you like to change any settings? (y/n): ", end='')
    if input().strip().lower() == 'y':
        # Human-in-the-loop
        print("\nEnable human approval for replies? (y/n): ", end='')
        state['human_in_the_loop'] = input().strip().lower() == 'y'

        # Auto-reply
        print("Enable auto-reply? (y/n): ", end='')
        auto_reply = input().strip().lower() == 'y'
        if 'watcher_config' not in state:
            state['watcher_config'] = {}
        state['watcher_config']['auto_reply_enabled'] = auto_reply

        # Poll interval
        print("Poll interval in seconds (default 5): ", end='')
        interval = input().strip()
        if interval.isdigit():
            state['watcher_config']['poll_interval_seconds'] = int(interval)

        # Save configuration
        with open('whatsapp_state.json', 'w') as f:
            json.dump(state, f, indent=2)

        print("\n✅ Configuration saved!")


def start_watcher():
    """Start the watcher in continuous mode."""
    print("\n" + "="*70)
    print("🚀 Starting WhatsApp Watcher")
    print("="*70)
    print("\nThe watcher will:")
    print("  1. Monitor incoming WhatsApp messages")
    print("  2. Generate AI responses using the assistant")
    print("  3. Send replies automatically (or with approval)")
    print("  4. Log all activity to whatsapp_state.json")
    print("\nPress Ctrl+C to stop the watcher")
    print("="*70)

    input("\nPress Enter to start...")

    watcher = WhatsAppWatcher()
    watcher.start()


def main():
    """Main menu for WhatsApp Watcher system."""
    while True:
        print("\n" + "="*70)
        print("🤖 WhatsApp Watcher System - Quick Start")
        print("="*70)
        print("\nOptions:")
        print("  1. Test all components")
        print("  2. Configure watcher settings")
        print("  3. Start watcher (continuous mode)")
        print("  4. Run watcher once (single iteration)")
        print("  5. View message history")
        print("  6. Exit")
        print("\nChoice: ", end='')

        choice = input().strip()

        if choice == '1':
            test_components()

        elif choice == '2':
            configure_watcher()

        elif choice == '3':
            start_watcher()

        elif choice == '4':
            print("\n🔄 Running single iteration...")
            watcher = WhatsAppWatcher()
            processed = watcher.run_once()
            print(f"\n✅ Processed {processed} message(s)")

        elif choice == '5':
            with open('whatsapp_state.json', 'r') as f:
                state = json.load(f)

            print("\n📊 Recent Activity:")
            print("\nIncoming Messages:")
            for msg in state.get('incoming_messages', [])[-5:]:
                print(f"  • [{msg.get('receivedAt')}] {msg.get('fromName')}: {msg.get('body')[:50]}...")

            print("\nPending Replies:")
            for reply in state.get('pending_replies', [])[-5:]:
                print(f"  • [{reply.get('status')}] To {reply.get('recipient')}: {reply.get('message')[:50]}...")

        elif choice == '6':
            print("\n👋 Goodbye!")
            break

        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    print("🤖 WhatsApp Watcher System")
    print("Make sure the Node.js server is running before starting!\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
