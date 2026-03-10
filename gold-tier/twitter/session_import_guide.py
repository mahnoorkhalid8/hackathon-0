"""
Twitter Session Import Helper
If automated login fails, use this to import your session from regular browser
"""

import json
from pathlib import Path

print("="*70)
print("Twitter Session Import - Manual Workaround")
print("="*70)
print("\nIf automated login keeps failing, follow these steps:\n")

print("STEP 1: Login to Twitter in your REGULAR browser")
print("  - Open Chrome or Edge (not the automated one)")
print("  - Go to: https://x.com")
print("  - Login with: khalidmahnoor889@gmail.com")
print("  - Make sure you're fully logged in\n")

print("STEP 2: Export cookies using browser extension")
print("  - Install: 'EditThisCookie' or 'Cookie-Editor' extension")
print("  - Click the extension icon on x.com")
print("  - Click 'Export' or 'Export All'")
print("  - Copy the JSON data\n")

print("STEP 3: Save cookies to file")
print("  - Create file: twitter_cookies.json")
print("  - Paste the exported cookies")
print("  - Save the file\n")

print("STEP 4: Run the converter")
print("  - python convert_cookies_to_session.py")
print("  - This will create twitter_session.json")
print("  - Next time you run twitter_personal_poster.py, it will auto-login!\n")

print("="*70)
print("\nAlternatively, try these simpler solutions first:")
print("  1. Use your Twitter @username instead of email")
print("  2. Clear browser cache and try again")
print("  3. Try from a different network (mobile hotspot)")
print("="*70)
