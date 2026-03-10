"""
Twitter Login Helper - Enhanced Anti-Detection
Run this to update your twitter_personal_poster.py with better anti-detection settings
"""

import re
from pathlib import Path

script_path = Path('twitter_personal_poster.py')
content = script_path.read_text(encoding='utf-8')

# Find and replace the browser launch section
old_launch = r'''browser = p\.chromium\.launch\(
                    channel='msedge',
                    headless=False,  # Visible mode for manual login and demo
                    args=\['--start-maximized'\]
                \)'''

new_launch = '''browser = p.chromium.launch(
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
                )'''

# Replace
content_new = re.sub(old_launch, new_launch, content, flags=re.MULTILINE)

if content_new != content:
    script_path.write_text(content_new, encoding='utf-8')
    print('[OK] Updated twitter_personal_poster.py with anti-detection settings')
    print('\nChanges made:')
    print('  - Disabled automation detection flags')
    print('  - Added browser security bypasses')
    print('  - Enhanced stealth mode')
    print('\nNow try running: python twitter_personal_poster.py')
else:
    print('[INFO] Could not find exact match to update')
    print('[INFO] Manual update needed')
