#!/usr/bin/env python3
"""
LinkedIn Skill: View Post History
Script to view recent LinkedIn posts and their status
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import dotenv

dotenv.load_dotenv()

def get_recent_posts(days=7):
    """
    Get recent LinkedIn posts from log files

    Args:
        days (int): Number of days to look back

    Returns:
        list: List of recent posts with their details
    """
    logs_dir = Path("Logs")

    # Look for recent log files
    target_date = datetime.now() - timedelta(days=days)
    recent_logs = []

    if logs_dir.exists():
        for log_file in logs_dir.glob(f"*linkedin.json"):
            # Extract date from filename (format: YYYY-MM-DD_linkedin.json)
            try:
                date_str = log_file.name.split('_')[0]  # Get the date part
                file_date = datetime.strptime(date_str, '%Y-%m-%d')

                if file_date >= target_date:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                        recent_logs.extend(logs)
            except (ValueError, json.JSONDecodeError):
                continue

    # Sort by timestamp (most recent first)
    recent_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return recent_logs


def view_linkedin_posts(days=7, limit=10):
    """
    View recent LinkedIn posts

    Args:
        days (int): Number of days to look back
        limit (int): Maximum number of posts to show

    Returns:
        dict: Result dictionary with posts and status
    """
    try:
        recent_posts = get_recent_posts(days)

        if not recent_posts:
            return {
                "success": True,
                "posts": [],
                "message": f"No LinkedIn posts found in the last {days} days"
            }

        # Limit the results
        limited_posts = recent_posts[:limit]

        return {
            "success": True,
            "posts": limited_posts,
            "total": len(recent_posts),
            "message": f"Found {len(recent_posts)} posts in the last {days} days, showing {len(limited_posts)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving LinkedIn posts: {str(e)}"
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="View recent LinkedIn posts")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of posts to show (default: 10)")

    args = parser.parse_args()

    result = view_linkedin_posts(args.days, args.limit)

    if result["success"]:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2))
        exit(1)