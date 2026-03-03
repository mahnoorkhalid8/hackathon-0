#!/usr/bin/env python3
"""Test if LinkedIn access token is valid"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('LINKEDIN_ACCESS_TOKEN')

if not token:
    print("[ERROR] No LinkedIn access token found")
    exit(1)

print(f"[INFO] Testing token: {token[:30]}...")

headers = {'Authorization': f'Bearer {token}'}

try:
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers, timeout=10)
    print(f"[INFO] Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] ✅ Token is VALID!")
        print(f"[INFO] Response: {response.json()}")
    else:
        print(f"[ERROR] Token invalid: {response.text[:300]}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
