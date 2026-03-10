"""
Twitter Session Saver - Ensures session is saved properly
Run this to login and save your session with extra verification
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

session_path = Path('twitter_session.json')
home_url = 'https://x.com/home'
login_url = 'https://x.com/i/flow/login'

print("="*70)
print("Twitter Session Saver - Guaranteed Session Persistence")
print("="*70)

with sync_playwright() as p:
    print("\n[1/5] Launching browser...")
    browser = p.chromium.launch(
        channel='msedge',
        headless=False,
        args=[
            '--start-maximized',
            '--disable-blink-features=AutomationControlled',
        ]
    )

    context = browser.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()

    print("[2/5] Navigating to Twitter...")
    page.goto(home_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    # Check if already logged in
    try:
        if page.locator('a[data-testid="AppTabBar_Home_Link"]').is_visible(timeout=3000):
            print("[OK] Already logged in!")
        else:
            raise Exception("Not logged in")
    except:
        print("[3/5] Please login to Twitter in the browser...")
        print("\nLogin steps:")
        print("  1. Enter your Twitter username or email")
        print("  2. Enter your password")
        print("  3. Complete 2FA if prompted")
        print("  4. Wait until you see your Twitter home feed")
        print("\nPress Enter AFTER you've successfully logged in...")
        input()

    print("\n[4/5] Verifying login...")
    time.sleep(3)

    # Verify login
    try:
        if page.locator('a[data-testid="AppTabBar_Home_Link"]').is_visible(timeout=5000):
            print("[OK] Login verified!")
        else:
            print("[ERROR] Login verification failed")
            print("Make sure you're on the Twitter home page")
            browser.close()
            sys.exit(1)
    except:
        print("[ERROR] Could not verify login")
        browser.close()
        sys.exit(1)

    print("\n[5/5] Saving session...")
    time.sleep(5)  # Extra wait to ensure all cookies are set

    try:
        context.storage_state(path=str(session_path))
        print(f"[SUCCESS] Session saved to: {session_path.absolute()}")

        # Verify file was created
        if session_path.exists():
            size = session_path.stat().st_size
            print(f"[VERIFIED] Session file exists ({size} bytes)")
            print("\n" + "="*70)
            print("SUCCESS! Next time you run twitter_personal_poster.py,")
            print("it will automatically login using this saved session.")
            print("="*70)
        else:
            print("[ERROR] Session file was not created!")
    except Exception as e:
        print(f"[ERROR] Failed to save session: {e}")
        browser.close()
        sys.exit(1)

    print("\nKeeping browser open for 10 seconds...")
    time.sleep(10)

    browser.close()
    print("\n[COMPLETE] Browser closed. Session saved successfully!")
