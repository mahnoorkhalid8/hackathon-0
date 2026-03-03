#!/usr/bin/env python3
"""Test posting a single post to debug"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
person_id = os.getenv('LINKEDIN_PERSON_ID', '547329244')
api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')

print(f"Token: {access_token[:30]}...")
print(f"Person ID: {person_id}")
print(f"API URL: {api_url}")
print()

# Load one post
posts_file = Path(__file__).parent / 'generated_posts.json'
with open(posts_file) as f:
    posts = json.load(f)

post = posts[0]
content = post['content']

print(f"Posting: {content[:100]}...")
print()

# Build post data with member URN
author_urn = f"urn:li:member:{person_id}"
print(f"Author URN: {author_urn}")
print()

post_data = {
    "author": author_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": content},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'X-Restli-Protocol-Version': '2.0.0'
}

print(f"Posting to: {api_url}ugcPosts")
print(f"Headers: {headers}")
print(f"Data: {json.dumps(post_data, indent=2)}")
print()

response = requests.post(
    f"{api_url}ugcPosts",
    headers=headers,
    json=post_data,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code in [200, 201]:
    print("\n✅ SUCCESS!")
else:
    print("\n❌ FAILED!")
