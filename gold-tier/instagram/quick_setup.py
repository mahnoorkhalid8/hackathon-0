"""
Quick Setup - Refresh Instagram Access Token
"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("Instagram Token Refresh - Quick Setup")
print("=" * 60)

# Load current env
env_path = Path("../.env")
load_dotenv(env_path)

app_id = os.getenv('FACEBOOK_APP_ID')
app_secret = os.getenv('FACEBOOK_APP_SECRET')

print("\nStep 1: Get a new short-lived token")
print("-" * 60)
print("1. Open: https://developers.facebook.com/tools/explorer/")
print("2. Select your app from dropdown")
print("3. Click 'Generate Access Token'")
print("4. Grant these permissions:")
print("   - instagram_basic")
print("   - instagram_content_publish")
print("   - pages_read_engagement")
print("   - pages_show_list")
print("5. Copy the token")
print("-" * 60)

short_token = input("\nPaste your token here: ").strip()

if not short_token:
    print("Error: No token provided")
    exit(1)

print("\nStep 2: Exchanging for long-lived token (60 days)...")

# Exchange for long-lived token
url = 'https://graph.facebook.com/v21.0/oauth/access_token'
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': app_id,
    'client_secret': app_secret,
    'fb_exchange_token': short_token
}

response = requests.get(url, params=params)
data = response.json()

if 'access_token' not in data:
    print(f"\nError: {data}")
    exit(1)

long_token = data['access_token']
expires_in = data.get('expires_in', 0)
days = int(expires_in) // 86400

print(f"\n✓ Success! Token expires in {days} days")

# Get Instagram Business Account ID
print("\nStep 3: Getting Instagram Business Account ID...")

page_id = os.getenv('FACEBOOK_PAGE_ID')
url = f'https://graph.facebook.com/v21.0/{page_id}'
params = {
    'fields': 'instagram_business_account',
    'access_token': long_token
}

response = requests.get(url, params=params)
data = response.json()

if 'instagram_business_account' in data:
    ig_id = data['instagram_business_account']['id']
    print(f"✓ Instagram Business Account ID: {ig_id}")
else:
    print("Warning: Could not get Instagram Business Account ID")
    print("Make sure your Facebook Page is connected to Instagram Business Account")
    ig_id = None

# Update .env file
print("\nStep 4: Updating .env file...")

env_content = env_path.read_text()
lines = env_content.split('\n')
updated_lines = []

for line in lines:
    if line.startswith('FACEBOOK_ACCESS_TOKEN='):
        updated_lines.append(f'FACEBOOK_ACCESS_TOKEN={long_token}')
    elif line.startswith('INSTAGRAM_ACCESS_TOKEN='):
        updated_lines.append(f'INSTAGRAM_ACCESS_TOKEN={long_token}')
    elif ig_id and line.startswith('INSTAGRAM_BUSINESS_ID='):
        updated_lines.append(f'INSTAGRAM_BUSINESS_ID={ig_id}')
    else:
        updated_lines.append(line)

env_path.write_text('\n'.join(updated_lines))

print("✓ .env file updated successfully!")
print("\n" + "=" * 60)
print("Setup Complete! You can now post to Instagram.")
print("=" * 60)
print("\nNext: Run the workflow manager to post your drafts")
print("Command: python ig_workflow_manager.py")
