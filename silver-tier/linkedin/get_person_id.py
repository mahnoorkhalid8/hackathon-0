#!/usr/bin/env python3
"""
Get your LinkedIn person URN/ID for posting

The LinkedIn API requires your person URN to post content.
This script helps you find your LinkedIn person ID.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

token = os.getenv('LINKEDIN_ACCESS_TOKEN')

if not token:
    print("[ERROR] No access token found in .env")
    exit(1)

print("=" * 70)
print("LinkedIn Person URN Finder")
print("=" * 70)
print()

# Method 1: Try different endpoints
endpoints = [
    ('https://api.linkedin.com/v2/emailAddress', 'Email Address'),
    ('https://api.linkedin.com/v2/me', 'Profile Info (me)'),
]

headers = {'Authorization': f'Bearer {token}'}

print("[INFO] Trying to fetch your LinkedIn info...")
print()

for url, name in endpoints:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"[{name}]")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Response: {data}")
            
            # Try to extract person ID
            if 'id' in data:
                print(f"  [SUCCESS] Person ID: {data['id']}")
            if 'elements' in data:
                for elem in data['elements']:
                    if 'id' in elem:
                        print(f"  [SUCCESS] Person ID: {elem['id']}")
        else:
            print(f"  Error: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"  Exception: {e}")
        print()

print("=" * 70)
print("ALTERNATIVE: Get your LinkedIn Person ID manually")
print("=" * 70)
print()
print("1. Open https://www.linkedin.com in your browser (while logged in)")
print("2. Open Developer Tools (Press F12)")
print("3. Go to Network tab")
print("4. Refresh the page")
print("5. Look for any request to 'api.linkedin.com'")
print("6. In the response, find your 'id' field - that's your person ID")
print()
print("Once you have your ID, update .env with:")
print("LINKEDIN_PERSON_ID=<your_person_id>")
print()
