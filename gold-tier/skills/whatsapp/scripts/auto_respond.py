"""
WhatsApp Auto-Respond Script

This script starts the AI-powered auto-responder that monitors
incoming messages and generates automatic replies.

Usage:
    python auto_respond.py
    python auto_respond.py --human-approval
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'whatsapp-node'))

# Import the main watcher module
from whatsapp_watcher import main

if __name__ == "__main__":
    print("="*70)
    print("WhatsApp Auto-Responder - Skills Interface")
    print("="*70)
    print()

    main()
