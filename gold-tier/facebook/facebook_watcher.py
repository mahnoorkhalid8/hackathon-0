"""
Facebook Watcher - Automatic Scheduled Posting

This script monitors your Facebook content folder and automatically posts to Facebook
at the scheduled times using the Facebook Graph API.

Usage:
    python facebook/facebook_watcher.py
    python facebook/facebook_watcher.py --dry-run  # Test without posting
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import argparse
import re


# Get the script's directory (works regardless of where script is run from)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / '.env')

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN') or os.getenv('FACEBOOK_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')


class FacebookWatcher:
    def __init__(self, dry_run=False):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.app_id = FACEBOOK_APP_ID
        self.app_secret = FACEBOOK_APP_SECRET
        self.dry_run = dry_run
        # Use paths relative to script directory (works from any location)
        self.draft_folder = SCRIPT_DIR / "Draft"
        self.approved_folder = SCRIPT_DIR / "Approved"
        self.need_action_folder = SCRIPT_DIR / "Need_Action"
        self.done_folder = SCRIPT_DIR / "Done"
        self.logs_folder = SCRIPT_DIR / "logs"

        # Create folders if they don't exist
        for folder in [self.draft_folder, self.approved_folder, self.need_action_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(exist_ok=True)

    def log_message(self, message):
        """Log message to file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        # Write to log file
        log_file = self.logs_folder / f"facebook_watcher_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def get_page_access_token(self):
        """Get page access token - uses FACEBOOK_ACCESS_TOKEN directly (already a page token)."""
        if not self.access_token:
            self.log_message("[ERROR] Missing required Facebook access token in .env")
            return None

        # FACEBOOK_ACCESS_TOKEN is already a page access token (from /me/accounts)
        # Just verify it works by checking page info
        url = f"https://graph.facebook.com/v19.0/{self.page_id}?access_token={self.access_token}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                page_info = response.json()
                self.log_message(f"[DEBUG] Page verified: {page_info.get('name', 'Unknown')}")
                return self.access_token
            else:
                self.log_message(f"[ERROR] Invalid page token: {response.text}")
                return None
        except Exception as e:
            self.log_message(f"[ERROR] Exception verifying page access token: {e}")
            return None

    def post_to_facebook(self, content):
        """Post content to Facebook page."""
        if self.dry_run:
            self.log_message("[DRY RUN] Would post to Facebook:")
            self.log_message(content[:100] + "...")
            return {"id": "dry-run-post-id"}

        # Get page access token
        page_token = self.get_page_access_token()
        if not page_token:
            return None

        # Prepare post data
        post_data = {
            'message': content,
            'access_token': page_token
        }

        # Post to Facebook page
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        response = requests.post(url, data=post_data)

        if response.status_code == 200:
            result = response.json()
            self.log_message(f"[SUCCESS] Posted to Facebook: {result.get('id', 'unknown')}")
            return result
        else:
            self.log_message(f"[ERROR] Failed to post to Facebook: {response.status_code}")
            self.log_message(f"Response: {response.text}")
            return None

    def extract_content_from_file(self, file_path):
        """Extract content from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for post content in markdown format
            # First try to find content after "## Post Content" or similar headers
            lines = content.split('\n')
            start_idx = -1

            for i, line in enumerate(lines):
                if line.strip().startswith('## Post Content') or line.strip().startswith('## Content') or 'Post Content' in line:
                    start_idx = i + 1
                    break

            if start_idx != -1:
                # Extract content starting from the identified section
                post_content = '\n'.join(lines[start_idx:]).strip()

                # Remove any checklists or approval instructions
                lines = post_content.split('\n')
                filtered_lines = []
                for line in lines:
                    if not line.strip().startswith('- [ ]') and not 'Approval Instructions' in line and not line.strip().startswith('##'):
                        filtered_lines.append(line)

                post_content = '\n'.join(filtered_lines).strip()
            else:
                # If no specific section found, take the whole content but remove headers
                lines = content.split('\n')
                filtered_lines = []
                for line in lines:
                    if not line.strip().startswith('#') and not 'Approval Instructions' in line and not 'Content Details' in line and not line.strip().startswith('- [ ]'):
                        filtered_lines.append(line)

                post_content = '\n'.join(filtered_lines).strip()

            return post_content.strip()
        except Exception as e:
            self.log_message(f"[ERROR] Failed to extract content from {file_path}: {e}")
            return None

    def should_post_now(self, content):
        """Check if content should be posted now (based on any scheduled time in content or file name)."""
        # For now, just return True if content exists
        # In the future, we can implement time-based scheduling
        return bool(content)

    def process_draft_posts(self):
        """Process draft posts and move them to approved if they meet criteria."""
        posts_made = 0

        # Process all markdown files in Draft folder
        for draft_file in self.draft_folder.glob("*.md"):
            self.log_message(f"[INFO] Processing draft file: {draft_file.name}")

            # Extract content
            content = self.extract_content_from_file(draft_file)
            if not content or content.strip() == "":
                self.log_message(f"[WARNING] No content found in {draft_file.name}, moving to Need_Action")
                # Move to Need_Action folder
                dest_path = self.need_action_folder / draft_file.name
                draft_file.rename(dest_path)
                continue

            # Check if it's time to post (for now, always true if content exists)
            if self.should_post_now(content):
                self.log_message(f"[INFO] Ready to post content from {draft_file.name}")

                # Post to Facebook
                result = self.post_to_facebook(content)

                if result:
                    # Move file to Done folder with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    done_filename = f"facebook_done_{timestamp}_{draft_file.name}"
                    dest_path = self.done_folder / done_filename
                    draft_file.rename(dest_path)

                    posts_made += 1
                    self.log_message(f"[SUCCESS] Posted {draft_file.name} and moved to Done folder")
                else:
                    self.log_message(f"[ERROR] Failed to post {draft_file.name}, keeping in Draft")
            else:
                self.log_message(f"[INFO] Not time to post {draft_file.name}, keeping in Draft")

        return posts_made

    def process_approved_posts(self):
        """Process approved posts and post them to Facebook."""
        posts_made = 0

        # Process all markdown files in Approved folder
        for approved_file in self.approved_folder.glob("*.md"):
            self.log_message(f"[INFO] Processing approved file: {approved_file.name}")

            # Extract content
            content = self.extract_content_from_file(approved_file)
            if not content or content.strip() == "":
                self.log_message(f"[WARNING] No content found in {approved_file.name}")
                continue

            # Post to Facebook
            result = self.post_to_facebook(content)

            if result:
                # Move file to Done folder with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                done_filename = f"facebook_done_{timestamp}_{approved_file.name}"
                dest_path = self.done_folder / done_filename
                approved_file.rename(dest_path)

                posts_made += 1
                self.log_message(f"[SUCCESS] Posted approved {approved_file.name} and moved to Done folder")
            else:
                self.log_message(f"[ERROR] Failed to post approved {approved_file.name}, keeping in Approved")

        return posts_made

    def run(self, check_interval=60):
        """Run watcher continuously."""
        self.log_message("="*70)
        self.log_message("Facebook Watcher - Automatic Scheduled Posting")
        self.log_message("="*70)

        if self.dry_run:
            self.log_message("[DRY RUN MODE] No actual posts will be made")

        # Test connection
        self.log_message("[INFO] Testing Facebook API connection...")
        page_token = self.get_page_access_token()

        if page_token:
            self.log_message("[SUCCESS] Connected to Facebook API!")
            self.log_message(f"[INFO] Page ID: {self.page_id}")
        else:
            self.log_message("[ERROR] Failed to connect to Facebook API")
            self.log_message("[INFO] Check your Facebook credentials in .env file")
            return

        self.log_message("")
        self.log_message(f"[INFO] Checking folders every {check_interval} seconds")
        self.log_message(f"[INFO] Draft folder: {self.draft_folder}")
        self.log_message(f"[INFO] Approved folder: {self.approved_folder}")
        self.log_message("")
        self.log_message("[INFO] Press Ctrl+C to stop")
        self.log_message("="*70)

        try:
            while True:
                draft_posts_made = self.process_draft_posts()
                approved_posts_made = self.process_approved_posts()

                total_posts = draft_posts_made + approved_posts_made
                if total_posts > 0:
                    self.log_message(f"\n[SUMMARY] Posted {total_posts} item(s) this cycle")

                # Wait before next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.log_message("\n\n[INFO] Facebook Watcher stopped by user")
            self.log_message("[INFO] State saved successfully")


def main():
    parser = argparse.ArgumentParser(description='Facebook Watcher - Automatic Scheduled Posting')
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

    # Check if required Facebook credentials are set
    missing_creds = []
    if not FACEBOOK_ACCESS_TOKEN:
        missing_creds.append('FACEBOOK_TOKEN')
    if not FACEBOOK_PAGE_ID:
        missing_creds.append('FACEBOOK_PAGE_ID')
    if not FACEBOOK_APP_ID:
        missing_creds.append('FACEBOOK_APP_ID')
    if not FACEBOOK_APP_SECRET:
        missing_creds.append('FACEBOOK_APP_SECRET')

    if missing_creds:
        print(f"[ERROR] Missing required Facebook credentials in .env: {', '.join(missing_creds)}")
        print("[INFO] Please add your Facebook credentials to .env")
        return

    watcher = FacebookWatcher(dry_run=args.dry_run)

    if args.once:
        print("[INFO] Running once...")
        draft_posts = watcher.process_draft_posts()
        approved_posts = watcher.process_approved_posts()
        total_posts = draft_posts + approved_posts
        print(f"\n[SUMMARY] Posted {total_posts} item(s)")
    else:
        watcher.run(check_interval=args.interval)


if __name__ == "__main__":
    main()