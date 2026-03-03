#!/usr/bin/env python3
"""
LinkedIn Simple Poster - Works without /me endpoint access

This version uses a direct LinkedIn posting approach that doesn't require
fetching user info first. It uses the token directly to post content.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_API_URL = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')
LINKEDIN_PERSON_ID = os.getenv('LINKEDIN_PERSON_ID')


def load_posts():
    """Load posts from generated_posts.json"""
    posts_file = Path(__file__).parent / 'generated_posts.json'
    
    try:
        with open(posts_file, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] {posts_file} not found")
        return []
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in {posts_file}")
        return []


def post_to_linkedin(content, person_id=None):
    """
    Post content to LinkedIn.
    
    Args:
        content: Post text content
        person_id: Your LinkedIn person ID (without urn:li:person: prefix)
    
    Returns:
        Response dict if successful, None otherwise
    """
    
    if not LINKEDIN_ACCESS_TOKEN:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not set in .env")
        return None
    
    if not person_id:
        person_id = LINKEDIN_PERSON_ID
    
    if not person_id:
        print("[ERROR] LINKEDIN_PERSON_ID not set in .env")
        print("[INFO] Please add your LinkedIn person ID to .env:")
        print("  LINKEDIN_PERSON_ID=your_id_here")
        return None
    
    headers = {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Prepare post data
    author_urn = f"urn:li:member:{person_id}"
    
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    url = f"{LINKEDIN_API_URL}ugcPosts"
    
    try:
        print(f"[INFO] Posting to LinkedIn...")
        response = requests.post(url, json=post_data, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            result = response.json()
            post_id = result.get('id', 'unknown')
            print(f"[SUCCESS] ✅ Post published! ID: {post_id}")
            return result
        else:
            print(f"[ERROR] Failed to post: {response.status_code}")
            print(f"[ERROR] Response: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None


def main():
    if not LINKEDIN_ACCESS_TOKEN:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env")
        return
    
    print("=" * 70)
    print("LinkedIn Simple Poster")
    print("=" * 70)
    print()
    
    posts = load_posts()
    
    if not posts:
        print("[ERROR] No posts found")
        return
    
    draft_posts = [p for p in posts if p.get('status') == 'draft']
    
    if not draft_posts:
        print("[INFO] No draft posts found")
        return
    
    print(f"[INFO] Found {len(draft_posts)} draft posts")
    print()
    
    # Check if person ID is set
    person_id = LINKEDIN_PERSON_ID
    if not person_id:
        print("[ERROR] LINKEDIN_PERSON_ID not set in .env")
        print()
        print("Please add your LinkedIn Person ID:")
        print("  1. Go to https://www.linkedin.com/in/yourprofile/")
        print("  2. Check the URL or page source for your numeric ID")
        print("  3. Add to .env: LINKEDIN_PERSON_ID=your_id")
        print()
        return
    
    print(f"[INFO] Using Person ID: {person_id}")
    print()
    
    # Post each draft
    posted_count = 0
    failed_count = 0
    
    for idx, post in enumerate(draft_posts, 1):
        post_id = post.get('id')
        pillar = post.get('pillar', 'unknown')
        content = post.get('content', '')
        
        print(f"[{idx}/{len(draft_posts)}] Posting #{post_id} ({pillar})...")
        
        result = post_to_linkedin(content, person_id)
        
        if result:
            post['status'] = 'posted'
            post['posted_at'] = datetime.now().isoformat()
            post['linkedin_post_id'] = result.get('id', '')
            posted_count += 1
            print(f"[✓] Success!")
        else:
            failed_count += 1
            print(f"[✗] Failed!")
        
        print()
    
    # Save updated posts
    posts_file = Path(__file__).parent / 'generated_posts.json'
    with open(posts_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print(f"[SUMMARY] Posted: {posted_count}, Failed: {failed_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
