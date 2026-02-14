#!/usr/bin/env python3
"""
Gmail API Test Script
Tests Gmail API configuration and sends a test email
"""

import os
import sys
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_credentials():
    """Test if credentials files exist"""
    print("=" * 60)
    print("GMAIL API CONFIGURATION TEST")
    print("=" * 60)
    print()

    # Load .env file
    load_env()

    # Get paths from environment
    creds_path = Path(os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"))
    token_path = Path(os.getenv("GMAIL_TOKEN_PATH", "token.json"))

    # Check credentials.json
    if creds_path.exists():
        print(f"✅ credentials.json found at: {creds_path}")
    else:
        print(f"❌ credentials.json NOT FOUND at: {creds_path}")
        print("   Check GMAIL_CREDENTIALS_PATH in .env file")
        return False

    # Check token.json
    if token_path.exists():
        print(f"✅ token.json found at: {token_path}")
    else:
        print(f"⚠️  token.json not found at: {token_path}")
        print("   (will be created on first run)")

    # Check .env
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file found")

        # Check CEO_EMAIL
        ceo_email = os.getenv("CEO_EMAIL")
        if ceo_email:
            print(f"✅ CEO_EMAIL configured: {ceo_email}")
        else:
            print("⚠️  CEO_EMAIL not found in .env")
    else:
        print("❌ .env file NOT FOUND")
        return False

    print()
    return True

def test_dependencies():
    """Test if required packages are installed"""
    print("=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    print()

    required_packages = [
        "google.auth",
        "google.oauth2",
        "googleapiclient",
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT INSTALLED")
            all_installed = False

    if not all_installed:
        print()
        print("Install missing packages:")
        print("  pip install -r requirements.txt")
        return False

    print()
    return True

def test_gmail_api():
    """Test Gmail API connection"""
    print("=" * 60)
    print("GMAIL API CONNECTION TEST")
    print("=" * 60)
    print()

    try:
        from gmail_api_service import GmailAPIService

        # Get paths from environment variables
        creds_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
        token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")

        print("Initializing Gmail API service...")
        gmail = GmailAPIService(credentials_path=creds_path, token_path=token_path)

        print("✅ Gmail API service initialized successfully")
        print("✅ Authentication successful")
        print()
        return True

    except FileNotFoundError as e:
        print(f"❌ Configuration error: {e}")
        print()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return False

def send_test_email():
    """Send a test email"""
    print("=" * 60)
    print("SEND TEST EMAIL")
    print("=" * 60)
    print()

    try:
        from gmail_api_service import GmailAPIService

        # Get CEO email from .env
        ceo_email = os.getenv("CEO_EMAIL", "khalidmahnoor889@gmail.com")

        print(f"Sending test email to: {ceo_email}")
        print()

        # Ask for confirmation
        response = input("Send test email? (y/n): ").strip().lower()
        if response != 'y':
            print("Test email cancelled")
            return False

        # Get paths from environment variables
        creds_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
        token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")

        # Initialize service
        gmail = GmailAPIService(credentials_path=creds_path, token_path=token_path)

        # Send test email
        result = gmail.send_email(
            to=ceo_email,
            subject="Gmail API Test - Silver Tier Digital FTE",
            body="""Hello!

This is a test email from the Silver Tier Digital FTE system.

If you received this email, your Gmail API configuration is working correctly!

System Details:
- Gmail API: Enabled
- OAuth2: Authenticated
- Email Service: Operational

Best regards,
Digital FTE System
"""
        )

        if result.get("success"):
            print()
            print("✅ Test email sent successfully!")
            print(f"   Message ID: {result.get('message_id')}")
            print(f"   Recipient: {ceo_email}")
            print()
            return True
        else:
            print()
            print(f"❌ Failed to send email: {result.get('error')}")
            print()
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return False

def main():
    """Run all tests"""
    print()
    print("🔧 Gmail API Configuration Test")
    print()

    # Load environment variables from .env file
    load_env()

    # Test 1: Check credentials
    if not test_credentials():
        print("❌ Configuration test failed")
        print()
        print("Next steps:")
        print("1. Check GMAIL_CREDENTIALS_PATH in .env file")
        print("2. Make sure credentials.json exists at that path")
        print("3. Run this test again")
        sys.exit(1)

    # Test 2: Check dependencies
    if not test_dependencies():
        print("❌ Dependency test failed")
        print()
        print("Next steps:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run this test again")
        sys.exit(1)

    # Test 3: Test Gmail API connection
    if not test_gmail_api():
        print("❌ Gmail API test failed")
        print()
        print("Next steps:")
        print("1. Make sure Gmail API is enabled in Google Cloud Console")
        print("2. Run: python run_agent.py ceo-report")
        print("3. Authenticate in browser")
        print("4. Run this test again")
        sys.exit(1)

    # Test 4: Send test email (optional)
    send_test_email()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print()
    print("✅ All tests passed!")
    print()
    print("Your Gmail API configuration is ready.")
    print()
    print("Available commands:")
    print("  python run_agent.py ceo-report    # Send CEO briefing")
    print("  python send_custom_email.py       # Send custom email")
    print()

if __name__ == "__main__":
    main()
