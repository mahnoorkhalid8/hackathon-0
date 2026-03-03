"""
LinkedIn Watcher - Automatic Scheduled Posting

This script monitors your content calendar and automatically posts to LinkedIn
at the scheduled times.

Usage:
    python linkedin_watcher.py
    python linkedin_watcher.py --dry-run  # Test without posting
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import argparse


# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_API_URL = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')


class LinkedInWatcher:
    def __init__(self, dry_run=False):
        self.access_token = LINKEDIN_ACCESS_TOKEN
        self.api_url = LINKEDIN_API_URL
        self.dry_run = dry_run
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.calendar_file = Path("content_calendar.json")
        self.posts_file = Path("generated_posts.json")
        self.state_file = Path("linkedin_watcher_state.json")

    def load_calendar(self):
        """Load content calendar."""
        if not self.calendar_file.exists():
            print(f"[ERROR] Calendar file not found: {self.calendar_file}")
            return []

        with open(self.calendar_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_posts(self):
        """Load generated posts."""
        if not self.posts_file.exists():
            print(f"[WARNING] Posts file not found: {self.posts_file}")
            return []

        with open(self.posts_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_state(self):
        """Load watcher state."""
        if not self.state_file.exists():
            return {"posted_items": [], "last_check": None}

        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_state(self, state):
        """Save watcher state."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def save_calendar(self, calendar):
        """Save updated calendar."""
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(calendar, f, indent=2, ensure_ascii=False)

    def get_user_info(self):
        """Get authenticated user information."""
        url = f"{self.api_url}me"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def post_to_linkedin(self, content):
        """Post content to LinkedIn."""
        if self.dry_run:
            print("[DRY RUN] Would post to LinkedIn:")
            print(content[:100] + "...")
            return {"id": "dry-run-post-id"}

        # Get user info
        user_info = self.get_user_info()
        if not user_info:
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
            return response.json()
        else:
            print(f"[ERROR] Failed to post: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def find_matching_post(self, calendar_item):
        """Find a matching post from generated_posts.json."""
        posts = self.load_posts()
        pillar = calendar_item.get('pillar', '')

        # Find first draft post matching the pillar
        for post in posts:
            if post.get('pillar') == pillar and post.get('status') == 'draft':
                return post

        return None

    def should_post_now(self, calendar_item):
        """Check if it's time to post this calendar item."""
        scheduled_datetime = calendar_item.get('datetime', '')

        if not scheduled_datetime:
            return False

        try:
            # Parse scheduled time
            scheduled_time = datetime.fromisoformat(scheduled_datetime.replace(' ', 'T'))
            current_time = datetime.now()

            # Check if we're within 5 minutes of scheduled time
            time_diff = abs((scheduled_time - current_time).total_seconds())

            # Post if within 5 minutes and not already posted
            return time_diff <= 300  # 5 minutes = 300 seconds

        except Exception as e:
            print(f"[ERROR] Failed to parse datetime: {e}")
            return False

    def process_calendar(self):
        """Process calendar and post scheduled items."""
        calendar = self.load_calendar()
        state = self.load_state()
        posted_items = state.get('posted_items', [])

        current_time = datetime.now()
        print(f"\n[INFO] Checking calendar at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        posts_made = 0

        for item in calendar:
            item_id = item.get('id')
            status = item.get('status', 'scheduled')

            # Skip if already posted
            if status == 'posted' or item_id in posted_items:
                continue

            # Check if it's time to post
            if self.should_post_now(item):
                print(f"\n[INFO] Time to post item #{item_id}")
                print(f"[INFO] Day: {item.get('day', 'N/A')}")
                print(f"[INFO] Pillar: {item.get('pillar', 'N/A')}")
                print(f"[INFO] Topic: {item.get('topic_type', 'N/A')}")

                # Find matching post
                post = self.find_matching_post(item)

                if not post:
                    print(f"[WARNING] No matching post found for pillar: {item.get('pillar')}")
                    print(f"[INFO] Generate posts with: python linkedin_post_generator.py --pillar {item.get('pillar')}")
                    continue

                # Get post content
                content = post.get('content', '')

                if not content:
                    print(f"[ERROR] Post content is empty")
                    continue

                # Post to LinkedIn
                print(f"[INFO] Posting to LinkedIn...")
                result = self.post_to_linkedin(content)

                if result:
                    # Update calendar item
                    item['status'] = 'posted'
                    item['posted_at'] = current_time.isoformat()
                    item['linkedin_post_id'] = result.get('id', '')

                    # Update post status
                    post['status'] = 'posted'
                    post['posted_at'] = current_time.isoformat()

                    # Save to posted items
                    posted_items.append(item_id)

                    posts_made += 1
                    print(f"[SUCCESS] Posted item #{item_id} successfully!")
                else:
                    print(f"[ERROR] Failed to post item #{item_id}")

        # Save updated state
        state['posted_items'] = posted_items
        state['last_check'] = current_time.isoformat()
        self.save_state(state)

        # Save updated calendar
        if posts_made > 0:
            self.save_calendar(calendar)

        return posts_made

    def run(self, check_interval=60):
        """Run watcher continuously."""
        print("="*70)
        print("LinkedIn Watcher - Automatic Scheduled Posting")
        print("="*70)
        print()

        if self.dry_run:
            print("[DRY RUN MODE] No actual posts will be made")
            print()

        # Test connection
        print("[INFO] Testing LinkedIn API connection...")
        user_info = self.get_user_info()

        if user_info:
            print("[SUCCESS] Connected to LinkedIn API!")
            print(f"[INFO] User: {user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}")
        else:
            print("[ERROR] Failed to connect to LinkedIn API")
            print("[INFO] Check your access token in .env file")
            return

        print()
        print(f"[INFO] Checking calendar every {check_interval} seconds")
        print(f"[INFO] Calendar file: {self.calendar_file}")
        print(f"[INFO] Posts file: {self.posts_file}")
        print()
        print("[INFO] Press Ctrl+C to stop")
        print("="*70)

        try:
            while True:
                posts_made = self.process_calendar()

                if posts_made > 0:
                    print(f"\n[SUMMARY] Posted {posts_made} item(s) this cycle")

                # Wait before next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n[INFO] Watcher stopped by user")
            print("[INFO] State saved successfully")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Watcher - Automatic Scheduled Posting')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - no actual posts will be made'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )

    args = parser.parse_args()

    # Check if access token is set
    if not LINKEDIN_ACCESS_TOKEN:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env file")
        print("[INFO] Please add your LinkedIn access token to .env")
        return

    watcher = LinkedInWatcher(dry_run=args.dry_run)

    if args.once:
        print("[INFO] Running once...")
        posts_made = watcher.process_calendar()
        print(f"\n[SUMMARY] Posted {posts_made} item(s)")
    else:
        watcher.run(check_interval=args.interval)


if __name__ == "__main__":
    main()
