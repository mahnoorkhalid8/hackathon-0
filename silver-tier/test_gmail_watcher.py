"""
Test/Demo Script for Gmail Watcher Service
Demonstrates Gmail watcher functionality with simulated emails.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_email_to_markdown():
    """Test email to markdown conversion."""
    print("="*70)
    print("  TEST: Email to Markdown Conversion")
    print("="*70)
    print()

    from gmail_watcher_service import EmailProcessor, GmailWatcherConfig

    config = GmailWatcherConfig()

    import logging
    logger = logging.getLogger("Test")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    processor = EmailProcessor(config, logger)

    # Simulated email
    test_email = {
        'id': 'test123',
        'thread_id': 'thread456',
        'sender': 'John Doe <john.doe@example.com>',
        'to': 'me@example.com',
        'subject': 'Test Email for Digital FTE',
        'date': datetime.now(),
        'body': '''Hello,

This is a test email to verify the Gmail watcher is working correctly.

Please process this email and create a task.

Best regards,
John Doe''',
        'snippet': 'This is a test email...',
        'labels': ['UNREAD', 'INBOX']
    }

    print("[Test] Processing simulated email...")
    print(f"  From: {test_email['sender']}")
    print(f"  Subject: {test_email['subject']}")
    print()

    success = processor.process_email(test_email)

    if success:
        print("[Test] [OK] Email processed successfully")
        print()

        # Find the created file
        inbox_path = Path(config.inbox_path)
        email_files = list(inbox_path.glob("email-*.md"))

        if email_files:
            latest_file = max(email_files, key=lambda p: p.stat().st_mtime)
            print(f"[Test] Created file: {latest_file}")
            print()
            print("[Test] File contents:")
            print("-" * 70)
            print(latest_file.read_text(encoding='utf-8'))
            print("-" * 70)
        else:
            print("[Test] [FAIL] No email file found")
    else:
        print("[Test] [FAIL] Email processing failed")

    print()


def test_configuration():
    """Test configuration loading."""
    print("="*70)
    print("  TEST: Configuration")
    print("="*70)
    print()

    from gmail_watcher_service import GmailWatcherConfig

    config = GmailWatcherConfig()

    print("[Test] Default configuration:")
    print(f"  Inbox path: {config.inbox_path}")
    print(f"  Check interval: {config.check_interval}s")
    print(f"  Max results: {config.max_results}")
    print(f"  Mark as read: {config.mark_as_read}")
    print(f"  Credentials file: {config.credentials_file}")
    print(f"  Token file: {config.token_file}")
    print(f"  Log level: {config.log_level}")
    print()

    # Test custom configuration
    custom_config = GmailWatcherConfig(
        inbox_path="custom/inbox",
        check_interval=60,
        max_results=20,
        mark_as_read=True
    )

    print("[Test] Custom configuration:")
    print(f"  Inbox path: {custom_config.inbox_path}")
    print(f"  Check interval: {custom_config.check_interval}s")
    print(f"  Max results: {custom_config.max_results}")
    print(f"  Mark as read: {custom_config.mark_as_read}")
    print()


def test_filename_generation():
    """Test filename generation."""
    print("="*70)
    print("  TEST: Filename Generation")
    print("="*70)
    print()

    from gmail_watcher_service import EmailProcessor, GmailWatcherConfig
    import logging

    config = GmailWatcherConfig()
    logger = logging.getLogger("Test")
    processor = EmailProcessor(config, logger)

    test_cases = [
        {
            'sender': 'John Doe <john@example.com>',
            'subject': 'Important: Project Update',
            'date': datetime(2026, 2, 13, 15, 30, 45)
        },
        {
            'sender': 'support@company.com',
            'subject': 'Re: Your Support Ticket #12345',
            'date': datetime(2026, 2, 13, 16, 45, 30)
        },
        {
            'sender': 'Newsletter <news@site.com>',
            'subject': 'Weekly Newsletter - February 2026',
            'date': datetime(2026, 2, 13, 10, 0, 0)
        }
    ]

    print("[Test] Testing filename generation:")
    print()

    for i, email in enumerate(test_cases, 1):
        filename = processor._generate_filename(email)
        print(f"Test {i}:")
        print(f"  From: {email['sender']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Filename: {filename}")
        print()


def check_prerequisites():
    """Check if prerequisites are met."""
    print("="*70)
    print("  Checking Prerequisites")
    print("="*70)
    print()

    # Check Python version
    import sys
    print(f"[Check] Python version: {sys.version}")

    # Check required libraries
    libraries = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient'
    ]

    all_installed = True
    for lib in libraries:
        try:
            __import__(lib)
            print(f"[Check] [OK] {lib} installed")
        except ImportError:
            print(f"[Check] [FAIL] {lib} NOT installed")
            all_installed = False

    print()

    if not all_installed:
        print("[Check] Missing libraries. Install with:")
        print("  pip install -r requirements_gmail.txt")
        print()

    # Check directories
    directories = ['vault/Inbox', 'config', 'logs']
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"[Check] [OK] {directory}/ exists")
        else:
            print(f"[Check] [MISS] {directory}/ missing (will be created)")

    print()

    # Check credentials
    creds_file = Path("config/gmail_credentials.json")
    if creds_file.exists():
        print("[Check] [OK] Gmail credentials file found")
    else:
        print("[Check] [MISS] Gmail credentials file NOT found")
        print("  Download from Google Cloud Console")
        print("  Save as: config/gmail_credentials.json")

    print()

    return all_installed


def main():
    """Run all tests."""
    print("\n")
    print("="*70)
    print("  Gmail Watcher Service - Test Suite")
    print("="*70)
    print("\n")

    # Check prerequisites
    if not check_prerequisites():
        print("[Test] Please install missing prerequisites first")
        return

    tests = [
        ("Configuration", test_configuration),
        ("Filename Generation", test_filename_generation),
        ("Email to Markdown", test_email_to_markdown)
    ]

    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[Test {i}/{len(tests)}] {name}")
        print()

        try:
            test_func()
        except Exception as e:
            print(f"\n[Error] Test failed: {e}")
            import traceback
            traceback.print_exc()

        if i < len(tests):
            print("\n" + "-"*70)
            print("  Press Enter to continue...")
            print("-"*70)
            try:
                input()
            except EOFError:
                pass

    print("\n" + "="*70)
    print("  Tests Complete")
    print("="*70)
    print()
    print("To run the actual service:")
    print("  1. Set up Gmail API credentials (see GMAIL_SETUP.md)")
    print("  2. Run: python gmail_watcher_service.py")
    print()


if __name__ == "__main__":
    main()
