"""
Upload image to Imgur and post to Instagram
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('../.env')

# Read image
with open('workflow/Drafts/post1_agentic_ai.jpg', 'rb') as f:
    image_data = f.read()

# Upload to Imgur (anonymous upload)
print("Uploading image to Imgur...")
headers = {'Authorization': 'Client-ID 546c25a59c58ad7'}  # Public Imgur client ID
response = requests.post(
    'https://api.imgur.com/3/image',
    headers=headers,
    files={'image': image_data}
)

if response.status_code == 200:
    imgur_url = response.json()['data']['link']
    print(f"Image uploaded: {imgur_url}")

    # Read caption
    with open('workflow/Drafts/post1_agentic_ai.md', 'r', encoding='utf-8') as f:
        caption = f.read().strip()

    # Post to Instagram
    print("\nPosting to Instagram...")
    from social_media_server import post_instagram_image
    result = post_instagram_image(imgur_url, caption)

    print(f"\nResult: {result}")
else:
    print(f"Imgur upload failed: {response.text}")
