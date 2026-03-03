"""
LinkedIn Auto Fix and Post Script

This script attempts to fix common LinkedIn API issues and post content.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime


def read_posts():
    """Read generated posts from JSON file."""
    try:
        with open('generated_posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
        return posts
    except Exception as e:
        print(f"Error reading posts: {e}")
        return []


def read_calendar():
    """Read content calendar from JSON file."""
    try:
        with open('content_calendar.json', 'r', encoding='utf-8') as f:
            calendar = json.load(f)
        return calendar
    except Exception as e:
        print(f"Error reading calendar: {e}")
        return []


def manual_post_workflow():
    """Manual posting workflow - display posts and guide user."""
    print("="*70)
    print("LINKEDIN MANUAL POSTING WORKFLOW")
    print("="*70)
    print()

    # Read posts
    posts = read_posts()
    calendar = read_calendar()

    print(f"Found {len(posts)} posts in generated_posts.json")
    print(f"Found {len(calendar)} calendar items in content_calendar.json")
    print()

    if not posts:
        print("No posts found. Generate some first:")
        print("  python linkedin_post_generator.py --pillar all --count 5")
        return

    # Show draft posts
    draft_posts = [p for p in posts if p.get('status') == 'draft']
    print(f"Draft posts available: {len(draft_posts)}")

    for post in draft_posts:
        print(f"  - ID: {post['id']}, Pillar: {post['pillar']}, Topic: {post['topic'][:30]}...")

    print()
    print("MANUAL POSTING INSTRUCTIONS:")
    print("1. Open generated_posts.json in a text editor")
    print("2. Copy the 'content' of each draft post")
    print("3. Go to LinkedIn and paste the content")
    print("4. Use LinkedIn's native scheduler for timing")
    print("5. Update post status to 'posted' manually")
    print()

    # Show content calendar timing
    if calendar:
        print("POSTING SCHEDULE FROM CALENDAR:")
        for item in calendar[:5]:  # Show first 5 items
            print(f"  - {item['day']} at {item['time']}: {item['pillar']}")
        if len(calendar) > 5:
            print(f"  ... and {len(calendar) - 5} more items")
        print()

    print("AUTOMATED SOLUTION:")
    print("If direct API posting fails, use Buffer app:")
    print("1. Go to buffer.com and sign up")
    print("2. Connect your LinkedIn account")
    print("3. Copy posts from generated_posts.json to Buffer")
    print("4. Buffer will post automatically to LinkedIn")
    print()


def update_post_status(post_id, new_status="posted"):
    """Update post status in generated_posts.json"""
    try:
        with open('generated_posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)

        for post in posts:
            if post['id'] == post_id:
                post['status'] = new_status
                post['posted_at'] = datetime.now().isoformat()
                break

        with open('generated_posts.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

        print(f"Post #{post_id} status updated to '{new_status}'")

    except Exception as e:
        print(f"Error updating post status: {e}")


def main():
    print("LinkedIn Auto Fix and Post Script")
    print("="*50)

    # Check if required files exist
    required_files = [
        'generated_posts.json',
        'content_calendar.json',
        'linkedin_poster.py',
        'linkedin_watcher.py'
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"Missing files: {missing_files}")
        return

    print("All required files found!")
    print()

    # Show available draft posts
    manual_post_workflow()

    print("For automatic posting when network allows:")
    print("1. Check your internet connection")
    print("2. Ensure no VPN/proxy is blocking LinkedIn API")
    print("3. Try running linkedin_watcher.py again")
    print()

    print("Temporary solution - manual posting:")
    print("- Use the content from generated_posts.json")
    print("- Post manually to LinkedIn")
    print("- Use Buffer.com for scheduled posting")
    print("- Update status using update_post_status(post_id)")


if __name__ == "__main__":
    main()