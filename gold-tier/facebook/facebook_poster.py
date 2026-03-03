"""
Facebook Poster - Direct Post to Facebook

This script allows direct posting to Facebook from a file or content string.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import argparse


# Get the script's directory (works regardless of where script is run from)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / '.env')

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN') or os.getenv('FACEBOOK_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')


def get_page_access_token():
    """Get page access token - uses FACEBOOK_ACCESS_TOKEN directly (already a page token)."""
    if not FACEBOOK_ACCESS_TOKEN:
        print("[ERROR] Missing required Facebook access token in .env")
        return None

    # FACEBOOK_ACCESS_TOKEN is already a page access token (from /me/accounts)
    # Just verify it works by checking page info
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            page_info = response.json()
            print(f"[DEBUG] Page verified: {page_info.get('name', 'Unknown')}")
            return FACEBOOK_ACCESS_TOKEN
        else:
            print(f"[ERROR] Invalid page token: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception verifying page access token: {e}")
        return None


def post_to_facebook(content):
    """Post content to Facebook page."""
    if not content.strip():
        print("[ERROR] Empty content provided")
        return None

    # Get page access token
    page_token = get_page_access_token()
    if not page_token:
        return None

    # Prepare post data
    post_data = {
        'message': content,
        'access_token': page_token
    }

    # Post to Facebook page
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"
    response = requests.post(url, data=post_data)

    if response.status_code == 200:
        result = response.json()
        print(f"[SUCCESS] Posted to Facebook: {result.get('id', 'unknown')}")
        return result
    else:
        print(f"[ERROR] Failed to post to Facebook: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def extract_content_from_file(file_path):
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
        print(f"[ERROR] Failed to extract content from {file_path}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Facebook Poster - Direct Post to Facebook')
    parser.add_argument(
        '--content',
        type=str,
        help='Direct content to post to Facebook'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Markdown file containing content to post to Facebook'
    )

    args = parser.parse_args()

    # Check if required Facebook credentials are set
    missing_creds = []
    if not FACEBOOK_ACCESS_TOKEN:
        missing_creds.append('FACEBOOK_TOKEN')
    if not FACEBOOK_PAGE_ID:
        missing_creds.append('FACEBOOK_PAGE_ID')

    if missing_creds:
        print(f"[ERROR] Missing required Facebook credentials in .env: {', '.join(missing_creds)}")
        print("[INFO] Please add your Facebook credentials to .env")
        return

    content = ""

    if args.content:
        content = args.content
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] File does not exist: {args.file}")
            return
        content = extract_content_from_file(file_path)
        if content is None:
            print(f"[ERROR] Could not extract content from {args.file}")
            return
    else:
        print("[ERROR] Please provide either --content or --file argument")
        return

    if not content.strip():
        print("[ERROR] No content to post")
        return

    print(f"[INFO] Posting to Facebook page: {FACEBOOK_PAGE_ID}")
    print(f"[INFO] Content preview: {content[:100]}...")
    print()

    result = post_to_facebook(content)

    if result:
        print(f"[SUCCESS] Post ID: {result.get('id', 'unknown')}")
    else:
        print("[ERROR] Failed to post to Facebook")


if __name__ == "__main__":
    main()