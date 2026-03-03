"""
WhatsApp Send Message Script

This script provides a simple interface to send WhatsApp messages
by selecting contacts by name.

Usage:
    python send_message.py
    python send_message.py --contact "John Doe" --message "Hello!"
"""

import sys
import os

# Add parent directory to path to import from whatsapp-node
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'whatsapp-node'))

# Import the main send_message module
from send_message import main

if __name__ == "__main__":
    print("="*70)
    print("WhatsApp Send Message - Skills Interface")
    print("="*70)
    print()

    main()
