"""
Gmail Send Email Script

This script provides a simple interface to send emails through Gmail
with support for attachments and HTML content.

Usage:
    python send_email.py
    python send_email.py --to "user@example.com" --subject "Test" --body "Hello"
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'gmail'))

try:
    from send_email import send_email as gmail_send_email
except ImportError:
    print("Error: Gmail implementation not found.")
    print("Make sure the gmail folder exists with send_email.py")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Send email via Gmail')
    parser.add_argument('--to', type=str, help='Recipient email address')
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--body', type=str, help='Email body')
    parser.add_argument('--cc', type=str, nargs='*', help='CC recipients')
    parser.add_argument('--bcc', type=str, nargs='*', help='BCC recipients')
    parser.add_argument('--attachments', type=str, nargs='*', help='File paths to attach')
    parser.add_argument('--html', action='store_true', help='Body is HTML')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    print("="*70)
    print("Gmail Send Email - Skills Interface")
    print("="*70)
    print()

    # Interactive mode
    if args.interactive or not (args.to and args.subject and args.body):
        print("Interactive Mode")
        print("-"*70)

        to = args.to or input("To: ").strip()
        subject = args.subject or input("Subject: ").strip()
        body = args.body or input("Body: ").strip()

        # Optional fields
        cc_input = input("CC (comma-separated, or press Enter to skip): ").strip()
        cc = cc_input.split(',') if cc_input else None

        bcc_input = input("BCC (comma-separated, or press Enter to skip): ").strip()
        bcc = bcc_input.split(',') if bcc_input else None

        attachments_input = input("Attachments (comma-separated paths, or press Enter to skip): ").strip()
        attachments = attachments_input.split(',') if attachments_input else None

        html_input = input("Is HTML? (yes/no): ").strip().lower()
        html = html_input in ['yes', 'y']
    else:
        to = args.to
        subject = args.subject
        body = args.body
        cc = args.cc
        bcc = args.bcc
        attachments = args.attachments
        html = args.html

    # Confirm
    print("\n" + "="*70)
    print("CONFIRM")
    print("="*70)
    print(f"To:      {to}")
    if cc:
        print(f"CC:      {', '.join(cc)}")
    if bcc:
        print(f"BCC:     {', '.join(bcc)}")
    print(f"Subject: {subject}")
    print(f"Body:    {body[:100]}{'...' if len(body) > 100 else ''}")
    if attachments:
        print(f"Attachments: {', '.join(attachments)}")
    print(f"HTML:    {html}")
    print("="*70)

    confirm = input("\nSend this email? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("\n[CANCELLED] Email not sent")
        return

    # Send email
    print("\nSending email...")
    try:
        result = gmail_send_email(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            html=html
        )

        if result.get('success'):
            print(f"\n[SUCCESS] Email sent!")
            print(f"Message ID: {result.get('message_id')}")
        else:
            print(f"\n[ERROR] Failed to send: {result.get('error')}")

    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
