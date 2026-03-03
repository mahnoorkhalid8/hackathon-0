"""
Facebook Token Helper

This script helps with Facebook token management and provides guidance
on how to refresh expired tokens.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_TOKEN = os.getenv('FACEBOOK_TOKEN')


def check_token_validity(token):
    """Check if the Facebook token is still valid."""
    url = f"https://graph.facebook.com/v19.0/me?access_token={token}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, str(e)


def refresh_long_lived_token(short_lived_token):
    """Convert a short-lived token to a long-lived token."""
    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
        return None, "Missing App ID or App Secret"

    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'fb_exchange_token': short_lived_token
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.text
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    print("="*60)
    print("Facebook Token Helper")
    print("="*60)

    if not FACEBOOK_TOKEN:
        print("[ERROR] No Facebook token found in .env file")
        print("Please add your Facebook token to the .env file as FACEBOOK_TOKEN")
    else:
        print(f"[INFO] Token found in .env file")
        print(f"[INFO] Token preview: {FACEBOOK_TOKEN[:20]}...")

        print("\n[INFO] Checking token validity...")
        is_valid, result = check_token_validity(FACEBOOK_TOKEN)

        if is_valid:
            print("[SUCCESS] Token is valid!")
            print(f"[INFO] Token details: {result}")
        else:
            print("[ERROR] Token is NOT valid!")
            print(f"[ERROR] Details: {result}")

            # Check if it's a short-lived token that can be refreshed
            if 'Invalid OAuth access token' in str(result) or 'Session has expired' in str(result):
                print("\n[INFO] Token appears to be expired.")
                print("You'll need to generate a new long-lived token using the Facebook Graph API.")

    print("\n" + "="*60)
    print("Token Renewal Instructions:")
    print("1. Go to Facebook Developers: https://developers.facebook.com/")
    print("2. Navigate to your app and get a new access token")
    print("3. Use the Graph API Explorer to generate a long-lived token")
    print("4. Or use the token exchange endpoint to refresh a short-lived token")
    print("="*60)