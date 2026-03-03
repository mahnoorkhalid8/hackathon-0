#!/usr/bin/env python3
"""
Custom Email Sender for Silver Tier Digital FTE
Sends formal emails using Gmail API

Usage:
    python send_custom_email.py                    # Uses draft-email.yaml
    python send_custom_email.py my-email.yaml      # Uses custom file
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from string import Template

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file at startup
load_env()


def load_email_draft(file_path: str) -> dict:
    """Load email content from YAML file"""
    draft_path = Path(file_path)

    if not draft_path.exists():
        print(f"❌ Draft file not found: {file_path}")
        print(f"\nCreate a draft file by copying draft-email.yaml:")
        print(f"  cp draft-email.yaml my-email.yaml")
        sys.exit(1)

    with open(draft_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_template() -> str:
    """Load email template"""
    template_path = Path("templates/formal-email-template.md")

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def fill_template(template: str, draft: dict) -> str:
    """Fill template with draft content"""
    return Template(template).safe_substitute(
        RECIPIENT_NAME=draft.get('recipient_name', ''),
        OPENING_PARAGRAPH=draft.get('opening', ''),
        MAIN_BODY=draft.get('body', ''),
        CLOSING_PARAGRAPH=draft.get('closing', ''),
        SENDER_NAME=draft.get('sender_name', ''),
        SENDER_TITLE=draft.get('sender_title', ''),
        COMPANY_NAME=draft.get('company_name', '')
    )


def send_email(to: str, subject: str, body: str) -> dict:
    """Send email via Gmail API"""
    try:
        from gmail_api_service import GmailAPIService

        # Get credentials path from config
        credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
        token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")

        # Initialize Gmail API service
        gmail = GmailAPIService(credentials_path=credentials_path, token_path=token_path)

        # Send email
        result = gmail.send_email(to=to, subject=subject, body=body)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point"""

    # Get draft file path from command line or use default
    if len(sys.argv) > 1:
        draft_file = sys.argv[1]
    else:
        draft_file = "draft-email.yaml"

    print()
    print("📧 Custom Email Sender")
    print("=" * 60)
    print()

    # Load draft
    print(f"Loading draft: {draft_file}")
    draft = load_email_draft(draft_file)

    # Validate required fields
    if not draft.get('to'):
        print("❌ Error: 'to' field is required in draft file")
        sys.exit(1)

    if not draft.get('subject'):
        print("❌ Error: 'subject' field is required in draft file")
        sys.exit(1)

    # Load template and fill with content
    template = load_template()
    email_body = fill_template(template, draft)

    # Show what we're sending
    print(f"To: {draft['to']}")
    print(f"Subject: {draft['subject']}")
    print()

    # Send email
    print(f"Sending email to {draft['to']}...")
    result = send_email(
        to=draft['to'],
        subject=draft['subject'],
        body=email_body
    )

    # Show result
    print()
    if result.get("success"):
        print("✅ Email sent successfully!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Failed to send email")
        print(f"   Error: {result.get('error')}")
        sys.exit(1)

    print()


if __name__ == "__main__":
    main()
