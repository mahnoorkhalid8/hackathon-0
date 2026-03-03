"""
LinkedIn Auto Poster

This script automatically posts content to LinkedIn using the LinkedIn API.
Reads posts from generated_posts.json and posts them automatically.

Usage:
    python linkedin_poster.py --post-id 1
    python linkedin_poster.py --post-all-drafts
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import argparse
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_API_URL = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')
LINKEDIN_PERSON_ID = os.getenv('LINKEDIN_PERSON_ID')  # Optional: Your LinkedIn person ID


class LinkedInPoster:
    def __init__(self):
        self.access_token = LINKEDIN_ACCESS_TOKEN
        self.api_url = LINKEDIN_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_user_info(self):
        """Get authenticated user information."""
        url = f"{self.api_url}me"
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Failed to get user info: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.Timeout:
            print("[ERROR] Connection timeout - LinkedIn API not responding")
            print("[INFO] Check your internet connection or try again later")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] Connection error: {e}")
            print("[INFO] Make sure you have internet access and LinkedIn is not blocked")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None

    def post_to_linkedin(self, content, author_urn=None):
        """
        Post content to LinkedIn.

        Args:
            content: Post text content
            author_urn: LinkedIn URN (e.g., urn:li:person:XXXXX or urn:li:organization:XXXXX)
        """
        # Get user info if author_urn not provided
        if not author_urn:
            # First, try to use LINKEDIN_PERSON_ID from env
            if LINKEDIN_PERSON_ID:
                author_urn = f"urn:li:person:{LINKEDIN_PERSON_ID}"
                print(f"[INFO] Using LinkedIn person ID from .env: {LINKEDIN_PERSON_ID}")
            else:
                # Try to get it from API
                user_info = self.get_user_info()
                if not user_info:
                    print("[ERROR] Failed to get user info. Please set LINKEDIN_PERSON_ID in .env")
                    print("[INFO] Run: python get_person_id.py")
                    return None
                author_urn = f"urn:li:person:{user_info['id']}"

        # Prepare post data
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

        # Post to LinkedIn
        url = f"{self.api_url}ugcPosts"
        response = requests.post(url, headers=self.headers, json=post_data)

        if response.status_code == 201:
            print(f"[SUCCESS] Post published to LinkedIn!")
            return response.json()
        else:
            print(f"[ERROR] Failed to post: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def post_to_company_page(self, content, organization_id):
        """
        Post content to LinkedIn company page.

        Args:
            content: Post text content
            organization_id: LinkedIn organization ID
        """
        author_urn = f"urn:li:organization:{organization_id}"
        return self.post_to_linkedin(content, author_urn)


def load_posts(file_path="generated_posts.json"):
    """Load posts from JSON file."""
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return []

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_posts(posts, file_path="generated_posts.json"):
    """Save posts to JSON file."""
    path = Path(file_path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def post_by_id(post_id):
    """Post a specific post by ID."""
    posts = load_posts()

    # Find post by ID
    post = next((p for p in posts if p.get('id') == post_id), None)

    if not post:
        print(f"[ERROR] Post #{post_id} not found")
        return False

    if post.get('status') == 'posted':
        print(f"[WARNING] Post #{post_id} already posted")
        return False

    # Post to LinkedIn
    poster = LinkedInPoster()
    content = post.get('content', '')

    print(f"\n[INFO] Posting to LinkedIn...")
    print(f"[INFO] Post ID: {post_id}")
    print(f"[INFO] Pillar: {post.get('pillar', 'unknown')}")
    print(f"[INFO] Topic: {post.get('topic', 'unknown')}")
    print()

    result = poster.post_to_linkedin(content)

    if result:
        # Update post status
        post['status'] = 'posted'
        post['posted_at'] = datetime.now().isoformat()
        post['linkedin_post_id'] = result.get('id', '')

        # Save updated posts
        save_posts(posts)

        print(f"[SUCCESS] Post #{post_id} published successfully!")
        return True
    else:
        print(f"[ERROR] Failed to post #{post_id}")
        return False


def post_all_drafts():
    """Post all draft posts."""
    posts = load_posts()

    # Filter draft posts
    drafts = [p for p in posts if p.get('status') == 'draft']

    if not drafts:
        print("[INFO] No draft posts found")
        return

    print(f"[INFO] Found {len(drafts)} draft posts")
    print()

    poster = LinkedInPoster()
    posted_count = 0
    failed_count = 0

    for post in drafts:
        post_id = post.get('id')
        content = post.get('content', '')

        print(f"[INFO] Posting #{post_id}...")

        result = poster.post_to_linkedin(content)

        if result:
            # Update post status
            post['status'] = 'posted'
            post['posted_at'] = datetime.now().isoformat()
            post['linkedin_post_id'] = result.get('id', '')
            posted_count += 1
            print(f"[SUCCESS] Post #{post_id} published!")
        else:
            failed_count += 1
            print(f"[ERROR] Failed to post #{post_id}")

        print()

    # Save updated posts
    save_posts(posts)

    print("="*70)
    print(f"[SUMMARY] Posted: {posted_count}, Failed: {failed_count}")
    print("="*70)


def list_posts():
    """List all posts with their status."""
    posts = load_posts()

    if not posts:
        print("[INFO] No posts found")
        return

    print("\n" + "="*70)
    print(f"{'ID':<5} {'Pillar':<15} {'Status':<10} {'Topic'}")
    print("="*70)

    for post in posts:
        post_id = str(post.get('id', ''))[:4]
        pillar = post.get('pillar', 'unknown')[:13]
        status = post.get('status', 'draft')[:8]
        topic = post.get('topic', 'N/A')[:30]

        print(f"{post_id:<5} {pillar:<15} {status:<10} {topic}")

    print("="*70)
    print(f"Total: {len(posts)} posts")

    # Count by status
    draft_count = len([p for p in posts if p.get('status') == 'draft'])
    posted_count = len([p for p in posts if p.get('status') == 'posted'])

    print(f"Draft: {draft_count}, Posted: {posted_count}")


def test_connection():
    """Test LinkedIn API connection."""
    print("[INFO] Testing LinkedIn API connection...")

    poster = LinkedInPoster()
    user_info = poster.get_user_info()

    if user_info:
        print("[SUCCESS] Connected to LinkedIn API!")
        print(f"[INFO] User ID: {user_info.get('id', 'N/A')}")
        print(f"[INFO] Name: {user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}")
        return True
    else:
        print("[ERROR] Failed to connect to LinkedIn API")
        print("[INFO] Check your access token in .env file")
        return False


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster')
    parser.add_argument('--post-id', type=int, help='Post specific post by ID')
    parser.add_argument('--post-all-drafts', action='store_true', help='Post all draft posts')
    parser.add_argument('--list', action='store_true', help='List all posts')
    parser.add_argument('--test', action='store_true', help='Test LinkedIn API connection')
    parser.add_argument('--organization-id', type=str, help='Post to company page (provide organization ID)')

    args = parser.parse_args()

    print("="*70)
    print("LinkedIn Auto Poster")
    print("="*70)
    print()

    # Check if access token is set
    if not LINKEDIN_ACCESS_TOKEN:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env file")
        print("[INFO] Please add your LinkedIn access token to .env")
        return

    if args.test:
        test_connection()
    elif args.list:
        list_posts()
    elif args.post_id:
        post_by_id(args.post_id)
    elif args.post_all_drafts:
        post_all_drafts()
    else:
        print("Usage:")
        print("  python linkedin_poster.py --test                    # Test API connection")
        print("  python linkedin_poster.py --list                    # List all posts")
        print("  python linkedin_poster.py --post-id 1               # Post specific post")
        print("  python linkedin_poster.py --post-all-drafts         # Post all drafts")
        print()


if __name__ == "__main__":
    main()
