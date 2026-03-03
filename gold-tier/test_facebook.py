"""
Test Facebook Integration

This script tests the Facebook API connection and posting functionality.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')


def test_connection():
    """Test Facebook API connection."""
    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        print("[ERROR] Missing required Facebook credentials in .env")
        print(f"FACEBOOK_TOKEN present: {bool(FACEBOOK_ACCESS_TOKEN)}")
        print(f"FACEBOOK_PAGE_ID present: {bool(FACEBOOK_PAGE_ID)}")
        return False

    # Test connection by getting page info
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            page_info = response.json()
            print(f"[SUCCESS] Connected to Facebook API!")
            print(f"[INFO] Page name: {page_info.get('name', 'Unknown')}")
            print(f"[INFO] Page ID: {page_info.get('id', 'Unknown')}")
            return True
        else:
            print(f"[ERROR] Failed to connect to Facebook API: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception testing Facebook connection: {e}")
        return False


def test_posting():
    """Test Facebook posting functionality."""
    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        print("[ERROR] Missing required Facebook credentials in .env")
        return False

    # Test posting a simple message
    message = f"Test post from AI Employee - {Path(__file__).parent.name} - {os.getcwd()}"
    post_data = {
        'message': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }

    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"

    try:
        response = requests.post(url, data=post_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Test post created successfully!")
            print(f"[INFO] Post ID: {result.get('id', 'Unknown')}")
            print(f"[INFO] Message: {message}")
            return True
        else:
            print(f"[ERROR] Failed to post to Facebook: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception testing Facebook posting: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Testing Facebook Integration")
    print("="*60)

    print("\n[INFO] Testing connection...")
    if test_connection():
        print("\n[INFO] Testing posting...")
        test_posting()
    else:
        print("\n[ERROR] Connection test failed, skipping posting test.")

    print("\n" + "="*60)
    print("Test completed")
    print("="*60)