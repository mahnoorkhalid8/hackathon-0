"""
Script to exchange short-lived token for long-lived token
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('../.env')

# Get your short-lived token from Graph API Explorer
SHORT_LIVED_TOKEN = input("Paste your short-lived token from Graph API Explorer: ").strip()

app_id = os.getenv('FACEBOOK_APP_ID')
app_secret = os.getenv('FACEBOOK_APP_SECRET')

# Exchange for long-lived token (60 days)
url = 'https://graph.facebook.com/v21.0/oauth/access_token'
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': app_id,
    'client_secret': app_secret,
    'fb_exchange_token': SHORT_LIVED_TOKEN
}

response = requests.get(url, params=params)
data = response.json()

if 'access_token' in data:
    long_lived_token = data['access_token']
    expires_in = data.get('expires_in', 'unknown')

    print(f"\n✓ Long-lived token generated!")
    print(f"Expires in: {expires_in} seconds (~{int(expires_in)//86400} days)")
    print(f"\nToken: {long_lived_token}")
    print(f"\nUpdate your .env file:")
    print(f"FACEBOOK_ACCESS_TOKEN={long_lived_token}")
    print(f"INSTAGRAM_ACCESS_TOKEN={long_lived_token}")
else:
    print(f"\n✗ Error: {data}")
