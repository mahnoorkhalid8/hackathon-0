"""
WhatsApp Check Status Script

This script checks WhatsApp connection status, account information,
and message statistics.

Usage:
    python check_status.py
    python check_status.py --detailed
    python check_status.py --json
"""

import sys
import os
import json
import argparse
import requests

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'whatsapp-node'))


def check_connection():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/status", timeout=5)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


def get_account_info():
    """Get account information."""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/info", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def get_statistics():
    """Get message statistics from state file."""
    try:
        state_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'whatsapp-node', 'whatsapp_state.json')
        with open(state_file, 'r') as f:
            state = json.load(f)
            return state.get('statistics', {})
    except Exception:
        return {}


def display_status(status_data, account_info, statistics, detailed=False):
    """Display status in formatted output."""
    print("\n" + "="*70)
    print("WhatsApp Status Check")
    print("="*70)

    # Connection status
    print(f"Connection:     {'Connected' if status_data.get('isReady') else 'Disconnected'}")
    print(f"Authenticated:  {'Yes' if status_data.get('isReady') else 'No'}")

    # Account info
    if account_info:
        print(f"Account:        {account_info.get('name')} ({account_info.get('number')})")
        print(f"Platform:       {account_info.get('platform', 'Unknown').title()}")

    # Session status
    print(f"Session Valid:  {'Yes' if not status_data.get('hasQR') else 'No (QR required)'}")

    # Statistics (if detailed)
    if detailed and statistics:
        print("\n" + "-"*70)
        print("Statistics:")
        print("-"*70)
        print(f"  Total Incoming:  {statistics.get('total_incoming', 0)}")
        print(f"  Total Sent:      {statistics.get('total_sent', 0)}")
        print(f"  Total Failed:    {statistics.get('total_failed', 0)}")
        print(f"  Total Approved:  {statistics.get('total_approved', 0)}")
        print(f"  Total Rejected:  {statistics.get('total_rejected', 0)}")

        # Calculate success rate
        total_incoming = statistics.get('total_incoming', 0)
        total_sent = statistics.get('total_sent', 0)
        if total_incoming > 0:
            success_rate = (total_sent / total_incoming) * 100
            print(f"  Success Rate:    {success_rate:.1f}%")

        # Last activity
        if statistics.get('last_message_received'):
            print(f"\n  Last Message Received: {statistics.get('last_message_received')}")
        if statistics.get('last_message_sent'):
            print(f"  Last Message Sent:     {statistics.get('last_message_sent')}")

    print("="*70)


def main():
    parser = argparse.ArgumentParser(description='Check WhatsApp status')
    parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    print("="*70)
    print("WhatsApp Check Status - Skills Interface")
    print("="*70)

    # Check connection
    connected, status_data = check_connection()

    if not connected:
        print(f"\n[ERROR] Cannot connect to WhatsApp backend")
        print(f"Error: {status_data}")
        print("\nMake sure:")
        print("  1. Node.js server is running (npm start)")
        print("  2. Server is on port 3000")
        return

    # Get account info
    account_info = get_account_info()

    # Get statistics
    statistics = get_statistics() if args.detailed else {}

    # Output
    if args.json:
        output = {
            "connected": connected,
            "status": status_data,
            "account": account_info,
            "statistics": statistics if args.detailed else None
        }
        print(json.dumps(output, indent=2))
    else:
        display_status(status_data, account_info, statistics, args.detailed)


if __name__ == "__main__":
    main()
