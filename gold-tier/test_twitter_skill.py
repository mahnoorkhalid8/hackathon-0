"""
Test Twitter Skill

This script tests the Twitter skill functionality.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path so we can import skills
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from skills.twitter_skill import execute_twitter_skill


def test_twitter_skill():
    """Test Twitter skill functions."""
    print("="*60)
    print("Testing Twitter Skill")
    print("="*60)

    # Test credentials check
    print("\n[INFO] Testing credentials...")
    result = execute_twitter_skill("check_credentials")
    print(f"Credentials check result: {result}")

    if result.get("success"):
        print("\n[INFO] Testing tweet posting...")
        result = execute_twitter_skill("post_tweet", text="Test tweet from AI Employee system!")
        print(f"Post tweet result: {result}")

        print("\n[INFO] Testing getting recent tweets...")
        result = execute_twitter_skill("get_tweets", limit=3)
        print(f"Get tweets result: {result}")
    else:
        print("\n[INFO] Twitter credentials not configured, skipping posting tests")

    print("\n" + "="*60)
    print("Twitter skill test completed")
    print("="*60)


if __name__ == "__main__":
    test_twitter_skill()