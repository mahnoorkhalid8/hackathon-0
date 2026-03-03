"""
Gmail Manage Labels Script

This script manages Gmail labels (folders) - create, delete, list, and apply to emails.

Usage:
    python manage_labels.py
    python manage_labels.py --action list
    python manage_labels.py --action create --label "Work"
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gmail'))

try:
    from manage_labels import manage_labels as gmail_manage_labels
except ImportError:
    print("Error: Gmail implementation not found.")
    print("Make sure the gmail folder exists with manage_labels.py")
    sys.exit(1)


def display_labels(labels):
    """Display labels in formatted output."""
    if not labels:
        print("No labels found.")
        return

    print("\n" + "="*70)
    print(f"{'Label Name':<40} {'Type':<15} {'Messages'}")
    print("="*70)

    for label in labels:
        name = label.get('name', 'Unknown')[:38]
        label_type = label.get('type', 'user')
        message_count = label.get('messagesTotal', 0)
        print(f"{name:<40} {label_type:<15} {message_count}")

    print("="*70)
    print(f"Total: {len(labels)} labels")


def main():
    parser = argparse.ArgumentParser(description='Manage Gmail labels')
    parser.add_argument('--action', type=str, choices=['list', 'create', 'delete', 'apply', 'remove'],
                       default='list', help='Action to perform')
    parser.add_argument('--label', type=str, help='Label name')
    parser.add_argument('--email-id', type=str, help='Email message ID (for apply/remove)')
    parser.add_argument('--color', type=str, help='Label color (for create)')

    args = parser.parse_args()

    print("="*70)
    print("Gmail Manage Labels - Skills Interface")
    print("="*70)
    print()

    try:
        if args.action == 'list':
            print("Listing all labels...")
            labels = gmail_manage_labels(action='list')
            display_labels(labels)

        elif args.action == 'create':
            if not args.label:
                print("[ERROR] --label is required for create action")
                return

            print(f"Creating label '{args.label}'...")
            result = gmail_manage_labels(
                action='create',
                label=args.label,
                color=args.color
            )

            if result.get('success'):
                print(f"[SUCCESS] Label '{args.label}' created")
                print(f"Label ID: {result.get('id')}")
            else:
                print(f"[ERROR] {result.get('error')}")

        elif args.action == 'delete':
            if not args.label:
                print("[ERROR] --label is required for delete action")
                return

            confirm = input(f"Delete label '{args.label}'? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("[CANCELLED]")
                return

            print(f"Deleting label '{args.label}'...")
            result = gmail_manage_labels(action='delete', label=args.label)

            if result.get('success'):
                print(f"[SUCCESS] Label '{args.label}' deleted")
            else:
                print(f"[ERROR] {result.get('error')}")

        elif args.action == 'apply':
            if not args.label or not args.email_id:
                print("[ERROR] --label and --email-id are required for apply action")
                return

            print(f"Applying label '{args.label}' to email...")
            result = gmail_manage_labels(
                action='apply',
                label=args.label,
                email_id=args.email_id
            )

            if result.get('success'):
                print(f"[SUCCESS] Label applied")
            else:
                print(f"[ERROR] {result.get('error')}")

        elif args.action == 'remove':
            if not args.label or not args.email_id:
                print("[ERROR] --label and --email-id are required for remove action")
                return

            print(f"Removing label '{args.label}' from email...")
            result = gmail_manage_labels(
                action='remove',
                label=args.label,
                email_id=args.email_id
            )

            if result.get('success'):
                print(f"[SUCCESS] Label removed")
            else:
                print(f"[ERROR] {result.get('error')}")

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
