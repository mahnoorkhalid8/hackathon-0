#!/usr/bin/env python3
"""
Fetch your LinkedIn Person ID using the access token
This bypasses CORS issues that occur in the browser
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
print("Fetching Your LinkedIn Person ID")
print("=" * 70)
print()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Try multiple endpoints
endpoints = [
    ('https://api.linkedin.com/v2/me', 'GET', 'Profile + Email'),
    ('https://api.linkedin.com/v2/userStatus', 'GET', 'User Status'),
]

person_id = None

for url, method, description in endpoints:
    print(f"[TRYING] {description}: {url}")
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [SUCCESS] Got response!")
            print(f"  Data: {data}")
            
            # Try to find person ID
            if 'id' in data:
                person_id = data['id']
                print(f"\n  🎯 FOUND PERSON ID: {person_id}")
                break
            
        else:
            print(f"  Error: {response.text[:300]}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    print()

if person_id:
    print("=" * 70)
    print("ADD THIS TO YOUR .env FILE:")
    print("=" * 70)
    print()
    print(f"LINKEDIN_PERSON_ID={person_id}")
    print()
    print("Then run:")
    print("python linkedin_poster.py --post-all-drafts")
    print()
else:
    print("=" * 70)
    print("Could not fetch automatically. Manual alternative:")
    print("=" * 70)
    print()
    print("1. Go to: https://www.linkedin.com/in/yourprofile/")
    print("2. Look at the page source (Ctrl+U) and search for:")
    print('   "entityUrn":"urn:li:person:')
    print("3. The number after 'urn:li:person:' is your ID")
    print()
    print("Or try the LinkedIn profile page to see if ID is visible in network tab")
    print()

