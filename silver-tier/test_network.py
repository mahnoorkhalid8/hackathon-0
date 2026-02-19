#!/usr/bin/env python3
"""Test network connectivity to LinkedIn API"""

import socket
import requests

print("=" * 70)
print("Network Connectivity Test")
print("=" * 70)
print()

# Test 1: DNS Resolution
print("[TEST 1] DNS Resolution for api.linkedin.com...")
try:
    ip = socket.gethostbyname('api.linkedin.com')
    print(f"[SUCCESS] ✅ Resolved to: {ip}")
except socket.gaierror as e:
    print(f"[ERROR] ❌ Failed to resolve: {e}")
print()

# Test 2: General internet connectivity
print("[TEST 2] General internet connectivity (Google DNS)...")
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print(f"[SUCCESS] ✅ Internet is reachable")
except Exception as e:
    print(f"[ERROR] ❌ Internet test failed: {e}")
print()

# Test 3: HTTPS connection to LinkedIn API
print("[TEST 3] HTTPS connection to api.linkedin.com...")
try:
    response = requests.head('https://api.linkedin.com', timeout=10)
    print(f"[SUCCESS] ✅ Connected! Status: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"[ERROR] ❌ Timeout connecting to LinkedIn API")
except requests.exceptions.ConnectionError as e:
    print(f"[ERROR] ❌ Connection error: {e}")
except Exception as e:
    print(f"[ERROR] ❌ Unexpected error: {e}")
print()

# Test 4: LinkedIn API with token
print("[TEST 4] LinkedIn API with authentication...")
try:
    from dotenv import load_dotenv
    import os
    from pathlib import Path
    
    load_dotenv(Path(__file__).parent / '.env')
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if not token:
        print("[ERROR] ❌ No access token found in .env")
    else:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://api.linkedin.com/v2/me', headers=headers, timeout=10)
        print(f"[SUCCESS] ✅ API authenticated! Status: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"[ERROR] ❌ Timeout - LinkedIn API not responding")
except requests.exceptions.ConnectionError as e:
    print(f"[ERROR] ❌ Connection error: {e}")
except Exception as e:
    print(f"[ERROR] ❌ Unexpected error: {e}")

print()
print("=" * 70)
print("TROUBLESHOOTING TIPS:")
print("=" * 70)
print("1. Check if you're connected to the internet")
print("2. If using a VPN, try disabling it")
print("3. Check if your firewall is blocking LinkedIn API")
print("4. Try accessing https://api.linkedin.com in your browser")
print("5. If all else fails, wait a few minutes and try again")
print("=" * 70)
