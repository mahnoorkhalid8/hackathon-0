"""
Gmail Search Emails Script

This script searches emails using Gmail's powerful search syntax.

Usage:
    python search_emails.py
    python search_emails.py --keyword "invoice"
    python search_emails.py --query "from:boss@company.com subject:urgent"
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gmail'))

try:
    from search_emails import search_emails as gmail_search_emails
except ImportError:
    print("Error: Gmail implementation not found.")
    print("Make sure the gmail folder exists with search_emails.py")
    sys.exit(1)


def display_results(emails):
    """Display search results in formatted output."""
    if not emails:
        print("No emails found matching your search.")
        return

    print("\n" + "="*70)
    print(f"Found {len(emails)} matching email(s)")
    print("="*70)

    for i, email in enumerate(emails, 1):
        print(f"\n{i}. From: {email.get('from', 'Unknown')}")
        print(f"   Subject: {email.get('subject', 'No subject')}")
        print(f"   Date: {email.get('date', 'Unknown')}")

        if email.get('has_attachment'):
            print(f"   Attachments: Yes")

        labels = email.get('labels', [])
        if labels:
            print(f"   Labels: {', '.join(labels)}")

        print(f"   Preview: {email.get('snippet', '')[:100]}...")
        print("-"*70)


def main():
    parser = argparse.ArgumentParser(description='Search Gmail emails')
    parser.add_argument('--query', type=str, help='Gmail search query')
    parser.add_argument('--keyword', type=str, help='Simple keyword search')
    parser.add_argument('--from', dest='from_email', type=str, help='Filter by sender')
    parser.add_argument('--to', type=str, help='Filter by recipient')
    parser.add_argument('--subject', type=str, help='Search in subject')
    parser.add_argument('--after', type=str, help='After date (YYYY-MM-DD)')
    parser.add_argument('--before', type=str, help='Before date (YYYY-MM-DD)')
    parser.add_argument('--has-attachment', action='store_true', help='Has attachments')
    parser.add_argument('--label', type=str, help='Filter by label')
    parser.add_argument('--limit', type=int, default=50, help='Maximum results')

    args = parser.parse_args()

    print("="*70)
    print("Gmail Search Emails - Skills Interface")
    print("="*70)
    print()

    # Build search query
    if args.query:
        print(f"Search Query: {args.query}")
    else:
        query_parts = []

        if args.keyword:
            query_parts.append(args.keyword)
            print(f"Keyword: {args.keyword}")

        if args.from_email:
            query_parts.append(f"from:{args.from_email}")
            print(f"From: {args.from_email}")

        if args.to:
            query_parts.append(f"to:{args.to}")
            print(f"To: {args.to}")

        if args.subject:
            query_parts.append(f"subject:{args.subject}")
            print(f"Subject: {args.subject}")

        if args.after:
            query_parts.append(f"after:{args.after.replace('-', '/')}")
            print(f"After: {args.after}")

        if args.before:
            query_parts.append(f"before:{args.before.replace('-', '/')}")
            print(f"Before: {args.before}")

        if args.has_attachment:
            query_parts.append("has:attachment")
            print(f"Has Attachments: Yes")

        if args.label:
            query_parts.append(f"label:{args.label}")
            print(f"Label: {args.label}")

        if not query_parts:
            print("No search criteria specified. Use --help for options.")
            return

        args.query = " ".join(query_parts)

    print(f"\nSearching...")

    try:
        emails = gmail_search_emails(
            query=args.query,
            limit=args.limit
        )

        display_results(emails)

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
