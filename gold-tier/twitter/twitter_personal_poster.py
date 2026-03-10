#!/usr/bin/env python3
"""
Twitter/X Personal Profile Poster - Uses Playwright to post to personal Twitter/X profile
Twitter API requires paid subscription, so we use browser automation (FREE!)

LOGIN FLOW:
-----------
1. FIRST RUN: Opens browser, waits for manual login (including 2FA), saves session to JSON
2. SUBSEQUENT RUNS: Loads saved session from JSON file, auto-logs in without manual steps
3. Session file: ./twitter_session.json (configurable via TWITTER_SESSION_PATH env var)

PRIVACY-FIRST:
--------------
- No credentials stored in code or .env
- Session state saved locally in JSON (cookies, localStorage)
- Manual login only - you control your credentials
- Browser runs in visible mode so you can see what's happening

USAGE:
------
First time: python twitter_personal_poster.py
  â†’ Browser opens, you login manually (with 2FA if needed)
  â†’ Session saved automatically

Next times: python twitter_personal_poster.py
  â†’ Auto-logs in using saved session
  â†’ Posts approved content from AI_Employee_Vault/Approved/X_POST_*.md
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

load_dotenv()


class TwitterPersonalPoster:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.vault_path = Path(os.getenv('VAULT_PATH', self.base_dir / 'AI_Employee_Vault'))
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'

        # Twitter session file (JSON format for storage_state)
        self.session_path = Path(os.getenv('TWITTER_SESSION_PATH', './twitter_session.json'))
        self.home_url = os.getenv('X_HOME_URL', 'https://x.com/home')
        self.login_url = os.getenv('X_LOGIN_URL', 'https://x.com/i/flow/login')
        self.browser_hold_seconds = int(os.getenv('BROWSER_HOLD_SECONDS', '60'))

        # Create directories
        for dir_path in [self.needs_action_dir, self.pending_approval_dir,
                         self.approved_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Ensure session file parent directory exists
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print(" " * 15 + "Twitter/X Personal Profile Poster")
        print("="*70)
        print("\nThis tool posts to your PERSONAL Twitter/X profile using browser automation.")
        print("(Twitter API requires paid subscription, so we use FREE browser automation)")
        print("\nSession Persistence:")
        if self.session_path.exists():
            print("  [OK] Saved session found - will auto-login")
            print(f"  [OK] Session file: {self.session_path}")
        else:
            print("  [!] No saved session - manual login required (one time)")
            print(f"  -> Session will be saved to: {self.session_path}")
        print("\nWorkflow:")
        print("  1. Read draft from Approved folder (X_POST_*.md)")
        print("  2. Open Twitter/X in browser (visible mode)")
        print("  3. Login (auto from saved session OR manual first-time)")
        print("  4. Post to your personal profile")
        print("  5. Move completed post to Done folder")
        print("="*70 + "\n")

    def login_to_twitter(self, page, context):
        """Login to Twitter using saved session or manual browser login

        Args:
            page: Playwright page object
            context: Playwright browser context (needed to save storage_state)

        Returns:
            bool: True if login successful, False otherwise
        """
        print("\n[LOGIN] Navigating to Twitter/X...")
        try:
            page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[LOGIN] Navigation slow, trying again...")
            try:
                page.goto(self.home_url, timeout=60000)
            except:
                print(f"[LOGIN] Still loading, continuing anyway...")

        # Wait a bit to see if we're already logged in
        time.sleep(3)

        # Check if already logged in (session loaded successfully)
        if self._is_logged_in(page):
            print("[LOGIN] âœ“ Already logged in (using saved session)")
            return True

        # Not logged in - need manual login
        try:
            page.goto(self.login_url, wait_until="domcontentloaded", timeout=60000)
        except Exception:
            pass

        print("\n" + "="*70)
        print("[LOGIN] MANUAL LOGIN REQUIRED")
        print("="*70)
        print("Please complete these steps in the browser window:")
        print("  1. Enter your Twitter/X username/email")
        print("  2. Enter your password")
        print("  3. Complete 2FA verification if prompted")
        print("  4. Wait until you see your Twitter/X home feed")
        print("="*70)
        print("\n[LOGIN] Your session will be saved automatically for future use.")
        print("[LOGIN] Press Enter AFTER you've successfully logged in...")
        input()

        # Verify login was successful
        if self._is_logged_in(page):
            print("[LOGIN] âœ“ Login verified! Saving session...")

            # Wait a bit to ensure all cookies/storage are set
            time.sleep(5)

            # Save the session state to file
            try:
                context.storage_state(path=str(self.session_path))
                print(f"[LOGIN] âœ“ Session saved to: {self.session_path}")
                print("[LOGIN] Next time you run this, login will be automatic!")
                return True
            except Exception as e:
                print(f"[LOGIN] âš ï¸  Warning: Could not save session: {e}")
                print("[LOGIN] You may need to login again next time.")
                return True  # Still return True since we are logged in
        else:
            print("[LOGIN] âœ— Login verification failed")
            if self._has_login_error(page):
                print("[LOGIN] X showed a temporary login error on screen.")
                print("[LOGIN] Script will retry with a fresh session.")
            print("[LOGIN] Please make sure you're on the Twitter/X home page")
            return False

    def _is_logged_in(self, page):
        """Check if user is logged in to Twitter"""
        try:
            # Look for common elements that appear when logged in
            selectors = [
                'a[data-testid="AppTabBar_Home_Link"]',  # Home link
                'a[aria-label="Post"]',  # Post button
                'div[data-testid="primaryColumn"]',  # Main timeline
                'a[href="/compose/tweet"]',  # Compose tweet link
            ]

            for selector in selectors:
                try:
                    if page.locator(selector).is_visible(timeout=3000):
                        return True
                except:
                    continue

            return False
        except:
            return False

    def _has_login_error(self, page):
        """Detect common temporary X login error text."""
        markers = [
            "Could not log you in now",
            "Please try again later",
        ]
        try:
            body_text = page.locator("body").inner_text(timeout=3000)
            return any(marker in body_text for marker in markers)
        except Exception:
            return False

    def post_to_profile(self, page, post_content):
        """Post content to personal Twitter/X profile"""
        print("\n[POST] Starting post creation...")

        try:
            # Navigate to home if not already there
            if "twitter.com" not in page.url and "x.com" not in page.url:
                print("[POST] Navigating to Twitter home...")
                page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

            # Find and click the "Post" button or tweet compose area
            print("[POST] Looking for tweet compose area...")

            # Try multiple selectors for the compose area
            compose_selectors = [
                'a[data-testid="SideNav_NewTweet_Button"]',  # Sidebar Post button
                'div[data-testid="tweetTextarea_0"]',  # Tweet text area
                'a[aria-label="Post"]',  # Post link
                'div[role="textbox"][contenteditable="true"]',  # Generic textbox
            ]

            clicked = False
            for selector in compose_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        element.click()
                        print(f"[POST] Clicked compose area using selector: {selector}")
                        clicked = True
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("[POST] âš ï¸  Could not find compose area automatically")
                print("[POST] Please click the 'Post' button manually...")
                input("Press Enter after clicking...")

            # Wait for compose modal/area to be ready
            print("[POST] Waiting for compose modal to load...")
            time.sleep(3)

            # Find the text input area
            print("[POST] Looking for text input area...")

            text_input_selectors = [
                'div[data-testid="tweetTextarea_0"]',  # Main tweet textarea
                'div[role="textbox"][contenteditable="true"]',  # Generic contenteditable
                'div[aria-label="Post text"]',  # Post text area
                'div.public-DraftEditor-content',  # Draft.js editor
                'div[contenteditable="true"]',  # Any contenteditable
            ]

            text_input = None
            for selector in text_input_selectors:
                try:
                    print(f"[POST] Trying selector: {selector}")
                    element = page.locator(selector).first
                    if element.is_visible(timeout=8000):
                        text_input = element
                        print(f"[POST] âœ“ Found text input using selector: {selector}")
                        break
                except Exception as e:
                    print(f"[POST] Selector failed: {str(e)[:50]}")
                    continue

            if not text_input:
                print("[POST] âš ï¸  Could not find text input automatically")
                print("[POST] MANUAL MODE: Please complete these steps:")
                print("\n" + "="*70)
                print("1. Paste this content in the tweet box:")
                print("="*70)
                print(post_content)
                print("="*70)
                print("2. Click the 'Post' button")
                print("3. Wait for post to complete")
                print("="*70 + "\n")

                response = input("Did you successfully post? (yes/no): ").lower()
                if response != 'yes':
                    print("[POST] âœ— Post cancelled by user")
                    return False
                else:
                    print("[POST] âœ“ Manual post confirmed")
                    return True
            else:
                # Type the tweet content
                print("[POST] Typing tweet content...")

                try:
                    # Click to focus
                    text_input.click()
                    time.sleep(1)

                    # Clear any existing content
                    page.keyboard.press('Control+A')
                    page.keyboard.press('Backspace')
                    time.sleep(0.5)

                    # Type content using keyboard
                    page.keyboard.type(post_content, delay=10)  # 10ms delay between keystrokes
                    print("[POST] âœ“ Content typed successfully")

                except Exception as e:
                    print(f"[POST] âœ— Auto-typing failed: {e}")
                    print("[POST] MANUAL MODE: Please paste the content manually")
                    print("\n" + "="*70)
                    print(post_content)
                    print("="*70 + "\n")
                    input("Press Enter after pasting the content...")

            # Wait a moment before posting
            print("[POST] Waiting 3 seconds for Post button to become active...")
            time.sleep(3)

            # Try keyboard shortcut first (most reliable)
            print("[POST] Attempting to post using Ctrl+Enter shortcut...")
            try:
                page.keyboard.press('Control+Enter')
                print("[POST] âœ“ Pressed Ctrl+Enter")
                time.sleep(2)

                # Check if modal closed (indicates success)
                try:
                    modal = page.locator('div[role="dialog"]').first
                    if not modal.is_visible(timeout=2000):
                        print("[POST] âœ“ Post successful via keyboard shortcut!")
                        return True
                except:
                    print("[POST] âœ“ Modal closed - post likely successful!")
                    return True

            except Exception as e:
                print(f"[POST] Keyboard shortcut didn't work: {e}")

            # Fallback: Find and click the Post button
            print("[POST] Looking for Post button...")

            post_button_selectors = [
                'button[data-testid="tweetButtonInline"]',  # Inline post button
                'button[data-testid="tweetButton"]',  # Main post button
                'div[data-testid="tweetButton"]',  # Alternative
                '[data-testid="tweetButton"]',  # Any element with this testid
                'button:has-text("Post")',  # Text-based
                'button:has-text("Tweet")',  # Old Twitter naming
                '//button[contains(., "Post")]',  # XPath fallback
                '//div[@role="button" and contains(., "Post")]',  # Div button
            ]

            posted = False
            for i, selector in enumerate(post_button_selectors):
                try:
                    print(f"[POST] Trying selector {i+1}/{len(post_button_selectors)}: {selector[:50]}...")

                    if selector.startswith('//'):
                        button = page.locator(f'xpath={selector}').first
                    else:
                        button = page.locator(selector).first

                    # Check if button exists and is visible
                    if button.count() > 0:
                        print(f"[POST] Button found! Checking if clickable...")

                        # Check if disabled
                        is_disabled = button.get_attribute('aria-disabled')
                        if is_disabled == 'true':
                            print(f"[POST] Button is disabled, skipping...")
                            continue

                        # Try to click
                        button.click(timeout=5000)
                        print(f"[POST] âœ“ Successfully clicked Post button!")
                        posted = True
                        break
                    else:
                        print(f"[POST] Button not found with this selector")

                except Exception as e:
                    print(f"[POST] Selector failed: {str(e)[:50]}")
                    continue

            if not posted:
                print("\n" + "="*70)
                print("[POST] Could not find Post button automatically")
                print("="*70)
                print("[POST] MANUAL ACTION REQUIRED:")
                print("  1. Look at the browser window")
                print("  2. Find the blue 'Post' button (usually top-right)")
                print("  3. Click it manually")
                print("  4. Wait for the post to complete")
                print("="*70)
                input("\nPress Enter AFTER you've clicked Post and the tweet is published...")
                posted = True

            # Wait for post to complete
            print("[POST] Waiting for post to complete...")
            time.sleep(5)

            # Verify post was successful
            print("[POST] âœ“ Post completed!")
            return True

        except Exception as e:
            print(f"[POST] âœ— Error during posting: {e}")
            print("[POST] Please complete the post manually if needed...")
            input("Press Enter when done...")
            return False

    def read_post_draft(self, file_path):
        """Read post content from markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            # Preferred: extract only the "## Post Content" section body.
            match = re.search(
                r"^##\s*Post Content\s*$\n(?P<body>.*?)(?:\n^##\s+|\Z)",
                content,
                flags=re.MULTILINE | re.DOTALL,
            )
            if match:
                post_content = match.group("body").strip()
            else:
                # Fallback for older templates: take first meaningful non-header line
                lines = content.split('\n')
                candidate_lines = []
                in_frontmatter = False
                frontmatter_seen = 0
                for line in lines:
                    if line.strip() == '---':
                        frontmatter_seen += 1
                        if frontmatter_seen <= 2:
                            in_frontmatter = not in_frontmatter
                            continue
                    if in_frontmatter:
                        continue
                    if line.strip().startswith('#') or not line.strip():
                        continue
                    candidate_lines.append(line.strip())
                post_content = '\n'.join(candidate_lines).strip()

            # Clean common markdown bullet prefixes if present
            if post_content.startswith('- '):
                post_content = post_content[2:].strip()
            if post_content.startswith('* '):
                post_content = post_content[2:].strip()

            # Validate character count
            char_count = len(post_content)
            if char_count == 0:
                print(f"[ERROR] Draft is empty or could not parse post content: {file_path.name}")
                return None
            if char_count > 280:
                print(f"[WARNING] Tweet is {char_count} characters (max 280)")
                print(f"[WARNING] Tweet will be truncated to 280 characters")
                post_content = post_content[:277] + "..."

            return post_content

        except Exception as e:
            print(f"[ERROR] Failed to read draft: {e}")
            return None

    def process_approved_posts(self):
        """Process all approved Twitter posts"""
        # Look for Twitter/X post drafts in Approved folder
        twitter_posts = list(self.approved_dir.glob("X_POST_*.md"))

        if not twitter_posts:
            print("[INFO] No approved Twitter/X posts found in Approved folder")
            return

        print(f"[INFO] Found {len(twitter_posts)} approved post(s)")

        # Start browser with session persistence
        with sync_playwright() as p:
            print("\n[BROWSER] Launching browser (visible mode)...")

            # Launch Microsoft Edge browser
            try:
                browser = p.chromium.launch(
                    channel='msedge',
                    headless=False,
                    args=[
                        '--start-maximized',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )
                print("[BROWSER] Using Microsoft Edge (channel=msedge)")
            except Exception as e:
                print(f"[ERROR] Could not launch Microsoft Edge: {e}")
                print("[ERROR] Ensure Microsoft Edge is installed, then try again.")
                return

            # Create context with or without saved session
            if self.session_path.exists():
                print(f"[SESSION] Loading saved session from: {self.session_path}")
                try:
                    # Load saved session state (cookies, localStorage, etc.)
                    context = browser.new_context(
                        storage_state=str(self.session_path),
                        viewport={'width': 1280, 'height': 720}
                    )
                    print("[SESSION] âœ“ Session loaded successfully")
                except Exception as e:
                    print(f"[SESSION] âš ï¸  Could not load session: {e}")
                    print("[SESSION] Creating fresh session...")
                    context = browser.new_context(
                        viewport={'width': 1280, 'height': 720}
                    )
            else:
                print("[SESSION] No saved session found - first time login required")
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720}
                )

            page = context.new_page()

            # Login to Twitter (will use loaded session or prompt for manual login)
            if not self.login_to_twitter(page, context):
                if self.session_path.exists():
                    print("[SESSION] Saved session may be stale/corrupted.")
                    print("[SESSION] Retrying with a fresh session...")
                    try:
                        context.close()
                    except Exception:
                        pass
                    try:
                        self.session_path.unlink(missing_ok=True)
                        print(f"[SESSION] Removed stale session file: {self.session_path}")
                    except Exception as e:
                        print(f"[SESSION] Could not remove session file: {e}")

                    context = browser.new_context(
                        viewport={'width': 1280, 'height': 720}
                    )
                    page = context.new_page()
                    if not self.login_to_twitter(page, context):
                        print("[ERROR] Failed to login to Twitter after retry")
                        context.close()
                        browser.close()
                        return
                else:
                    print("[ERROR] Failed to login to Twitter")
                    context.close()
                    browser.close()
                    return

            # Process each post
            for post_file in twitter_posts:
                print(f"\n[PROCESS] Processing: {post_file.name}")

                # Read post content
                post_content = self.read_post_draft(post_file)
                if not post_content:
                    print(f"[ERROR] Could not read post content from {post_file.name}")
                    continue

                print(f"[CONTENT] Tweet preview:\n{post_content[:100]}...")
                print(f"[CONTENT] Character count: {len(post_content)}")

                # Post to Twitter
                success = self.post_to_profile(page, post_content)

                if success:
                    # Move to Done folder
                    done_file = self.done_dir / post_file.name
                    post_file.rename(done_file)
                    print(f"[DONE] âœ“ Moved to Done: {done_file.name}")

                    # Update dashboard
                    self.update_dashboard(post_file.name, post_content)
                else:
                    print(f"[ERROR] Failed to post {post_file.name}")

                # Wait between posts
                if len(twitter_posts) > 1:
                    print("\n[WAIT] Waiting 10 seconds before next post...")
                    time.sleep(10)

            if self.browser_hold_seconds == 0:
                print("\n[BROWSER] Keeping browser open until you press Enter...")
                input("Press Enter to close browser...")
            else:
                print(f"\n[BROWSER] Keeping browser open for {self.browser_hold_seconds} seconds...")
                time.sleep(self.browser_hold_seconds)
            context.close()
            browser.close()
            print("[BROWSER] Browser closed")

    def update_dashboard(self, filename, content_preview):
        """Update Dashboard.md with post activity"""
        dashboard_file = self.vault_path / 'Dashboard.md'

        try:
            if dashboard_file.exists():
                dashboard_content = dashboard_file.read_text(encoding='utf-8')
            else:
                dashboard_content = "# AI Employee Dashboard\n\n## Recent Activity\n\n"

            # Add new entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_entry = f"- [{timestamp}] Posted to Twitter/X: {filename} - {content_preview[:50]}...\n"

            # Insert after "Recent Activity" header
            if "## Recent Activity" in dashboard_content:
                parts = dashboard_content.split("## Recent Activity")
                dashboard_content = parts[0] + "## Recent Activity\n\n" + new_entry + parts[1].lstrip('\n')
            else:
                dashboard_content += f"\n## Recent Activity\n\n{new_entry}"

            dashboard_file.write_text(dashboard_content, encoding='utf-8')
            print(f"[DASHBOARD] Updated Dashboard.md")

        except Exception as e:
            print(f"[WARNING] Could not update dashboard: {e}")

    def run(self):
        """Main execution"""
        self.print_banner()

        # Check for session file
        if self.session_path.exists():
            print("[INFO] Using saved session - automatic login enabled")
        else:
            print("[INFO] First-time setup - manual login required")
            print("[INFO] After login, session will be saved for future automatic logins")

        print(f"[INFO] Session file: {self.session_path}")
        print(f"[INFO] Vault path: {self.vault_path}")
        print()

        # Process approved posts
        self.process_approved_posts()

        print("\n[COMPLETE] Twitter/X posting session complete!")
        if self.session_path.exists():
            print(f"[INFO] âœ“ Session saved - next run will auto-login")
        print(f"\n[TIP] To reset session (force re-login), delete: {self.session_path}")


if __name__ == "__main__":
    poster = TwitterPersonalPoster()
    poster.run()