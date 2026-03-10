"""
Twitter Poster - Improved with Keyboard Shortcuts
More reliable than clicking - uses keyboard shortcuts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from twitter_personal_poster import TwitterPersonalPoster
from playwright.sync_api import sync_playwright
import time

class ImprovedTwitterPoster(TwitterPersonalPoster):
    """Improved version with keyboard shortcuts"""

    def post_to_profile(self, page, post_content):
        """Post using keyboard shortcuts - more reliable than clicking"""
        print("\n[POST] Starting post creation with keyboard shortcuts...")

        try:
            # Navigate to home if needed
            if "twitter.com" not in page.url and "x.com" not in page.url:
                print("[POST] Navigating to Twitter home...")
                page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)

            print("[POST] Using keyboard shortcut to open compose...")

            # Method 1: Press 'N' key (Twitter shortcut to compose new tweet)
            print("[POST] Pressing 'N' to open compose modal...")
            page.keyboard.press('n')
            time.sleep(3)

            # Method 2: If that didn't work, try clicking anywhere and then 'N'
            try:
                page.click('body')
                time.sleep(1)
                page.keyboard.press('n')
                time.sleep(3)
            except:
                pass

            print("[POST] Typing tweet content...")

            # Type the content directly (keyboard will go to focused element)
            page.keyboard.type(post_content, delay=50)

            print("[POST] Content typed successfully!")
            print("[POST] Waiting 3 seconds before posting...")
            time.sleep(3)

            # Post using Ctrl+Enter (Twitter shortcut)
            print("[POST] Pressing Ctrl+Enter to post...")
            page.keyboard.press('Control+Enter')

            print("[POST] Waiting for post to complete...")
            time.sleep(5)

            print("[POST] ✓ Post completed!")
            return True

        except Exception as e:
            print(f"[POST] Error: {e}")
            print("\n[POST] FALLBACK: Manual posting required")
            print("="*70)
            print("Please complete these steps:")
            print("1. Press 'N' key to open compose")
            print("2. Paste this content:")
            print("="*70)
            print(post_content)
            print("="*70)
            print("3. Press Ctrl+Enter to post")
            print("="*70)

            response = input("\nDid you successfully post? (yes/no): ").lower()
            return response == 'yes'

if __name__ == "__main__":
    poster = ImprovedTwitterPoster()
    poster.run()
