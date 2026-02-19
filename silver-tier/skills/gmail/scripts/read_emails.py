"""
Gmail Read Emails Script

This script reads and filters emails from Gmail inbox with various options.

Usage:
    python read_emails.py
    python read_emails.py --unread --limit 10
    python read_emails.py --sender "boss@company.com"
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gmail'))

try:
    from read_emails import read_emails as gmail_read_emails
except ImportError:
    print("Error: Gmail implementation not found.")
    print("Make sure the gmail folder exists with read_emails.py")
    sys.exit(1)


def display_emails(emails):
    """Display emails in formatted output."""
    if not emails:
        print("No emails found.")
        return

    print("\n" + "="*70)
    print(f"Found {len(emails)} email(s)")
    print("="*70)

    for i, email in enumerate(emails, 1):
        print(f"\n{i}. From: {email.get('from', 'Unknown')}")
        print(f"   Subject: {email.get('subject', 'No subject')}")
        print(f"   Date: {email.get('date', 'Unknown')}")
        print(f"   Preview: {email.get('snippet', '')[:100]}...")
        if email.get('unread'):
            print(f"   Status: UNREAD")
        print("-"*70)


def main():
    parser = argparse.ArgumentParser(description='Read Gmail emails')
    parser.add_argument('--unread', action='store_true', help='Only show unread emails')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of emails')
    parser.add_argument('--sender', type=str, help='Filter by sender email')
    parser.add_argument('--subject', type=str, help='Filter by subject keywords')
    parser.add_argument('--after', type=str, help='Show emails after date (YYYY-MM-DD)')
    parser.add_argument('--before', type=str, help='Show emails before date (YYYY-MM-DD)')
    parser.add_argument('--label', type=str, help='Filter by Gmail label')
    parser.add_argument('--mark-read', action='store_true', help='Mark retrieved emails as read')

    args = parser.parse_args()

    print("="*70)
    print("Gmail Read Emails - Skills Interface")
    print("="*70)
    print()

    # Build filters
    print("Reading emails...")
    if args.unread:
        print("  Filter: Unread only")
    if args.sender:
        print(f"  Filter: From {args.sender}")
    if args.subject:
        print(f"  Filter: Subject contains '{args.subject}'")
    if args.after:
        print(f"  Filter: After {args.after}")
    if args.before:
        print(f"  Filter: Before {args.before}")
    if args.label:
        print(f"  Filter: Label '{args.label}'")

    try:
        emails = gmail_read_emails(
            unread_only=args.unread,
            limit=args.limit,
            sender=args.sender,
            subject=args.subject,
            after=args.after,
            before=args.before,
            label=args.label,
            mark_read=args.mark_read
        )

        display_emails(emails)

        if args.mark_read and emails:
            print(f"\n[OK] Marked {len(emails)} email(s) as read")

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
