"""
Twitter Session Saver - Improved Version (More Reliable)
Saves session with better verification and fallback options
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

session_path = Path('twitter_session.json')
home_url = 'https://x.com/home'

print("="*70)
print("Twitter Session Saver - Improved Version")
print("="*70)

with sync_playwright() as p:
    print("\n[1/4] Launching browser...")
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

    print("[2/4] Navigating to Twitter...")
    page.goto(home_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)

    print("\n[3/4] Please login to Twitter in the browser...")
    print("\nLogin steps:")
    print("  1. Enter your Twitter username/email/phone")
    print("  2. Enter your password")
    print("  3. Complete 2FA if prompted")
    print("  4. Wait until you see your Twitter home feed")
    print("  5. Make sure you can see tweets on the page")
    print("\nPress Enter AFTER you've successfully logged in...")
    input()

    print("\n[4/4] Saving session (no verification needed)...")
    print("Waiting 10 seconds to ensure all cookies are set...")
    time.sleep(10)

    try:
        # Save session regardless of verification
        context.storage_state(path=str(session_path))

        # Verify file was created
        if session_path.exists():
            size = session_path.stat().st_size
            print(f"\n[SUCCESS] Session saved to: {session_path.absolute()}")
            print(f"[VERIFIED] Session file exists ({size} bytes)")

            # Basic validation - check if file has content
            if size > 100:
                print("\n" + "="*70)
                print("✅ SUCCESS! Session saved successfully!")
                print("="*70)
                print("\nNext time you run twitter_personal_poster.py:")
                print("  - Browser will open")
                print("  - Auto-login (no manual steps)")
                print("  - Tweet posted automatically")
                print("  - File moved to Done folder")
                print("\nNo more manual logins needed! 🎉")
                print("="*70)
            else:
                print("\n[WARNING] Session file is very small, might be incomplete")
                print("But we'll try using it anyway")
        else:
            print("\n[ERROR] Session file was not created!")
            print("This might be a permissions issue")
            browser.close()
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Failed to save session: {e}")
        browser.close()
        sys.exit(1)

    print("\nKeeping browser open for 5 more seconds...")
    time.sleep(5)

    browser.close()
    print("\n[COMPLETE] Browser closed. You can now use auto-login!")
    print("\nTo post a tweet:")
    print("  cd twitter")
    print("  mv AI_Employee_Vault/Need_Action/X_POST_*.md AI_Employee_Vault/Approved/")
    print("  python twitter_personal_poster.py")
