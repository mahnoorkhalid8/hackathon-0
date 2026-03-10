"""
Get Instagram Business Account ID after connecting to Facebook Page
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv('../.env', override=True)

access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')

print("Fetching Instagram Business Account ID...")
print(f"Facebook Page ID: {page_id}\n")

url = f'https://graph.facebook.com/v21.0/{page_id}'
params = {
    'fields': 'instagram_business_account',
    'access_token': access_token
}

response = requests.get(url, params=params)
data = response.json()

if 'instagram_business_account' in data:
    ig_id = data['instagram_business_account']['id']
    print(f"[SUCCESS] Instagram Business Account ID: {ig_id}\n")

    # Update .env file
    env_path = Path('../.env')
    env_content = env_path.read_text()
    lines = env_content.split('\n')
    updated = []

    for line in lines:
        if line.startswith('INSTAGRAM_BUSINESS_ID='):
            updated.append(f'INSTAGRAM_BUSINESS_ID={ig_id}')
        else:
            updated.append(line)

    env_path.write_text('\n'.join(updated))
    print("[OK] Updated .env file with correct Instagram Business Account ID")
    print("\nYou can now post to Instagram!")
else:
    print("[ERROR] No Instagram Business Account found")
    print("\nYour Facebook Page is not connected to an Instagram Business Account.")
    print("\nTo fix:")
    print("1. Go to: https://www.facebook.com/settings?tab=instagram")
    print("2. Connect your Instagram Business Account")
    print("3. Run this script again")
