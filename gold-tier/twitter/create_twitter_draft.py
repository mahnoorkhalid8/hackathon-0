#!/usr/bin/env python3
"""Twitter/X Post Draft Generator - Creates Twitter/X post drafts for your personal poster"""

import sys
from pathlib import Path
from datetime import datetime
import hashlib


def create_twitter_draft(content, title="Twitter/X Post Draft"):
    """Create Twitter/X post draft in Need_Action folder"""
    base_dir = Path(__file__).parent.resolve()
    need_action = base_dir / 'Need_Action'
    need_action.mkdir(exist_ok=True)

    # Generate unique ID
    post_id = hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:8]
    filename = f"X_POST_{post_id}.md"
    filepath = need_action / filename

    # Create draft
    draft = f"""---
type: twitter_post
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: needs_action
character_count: {len(content)}
max_chars: 280
---

# {title}

## Post Content
{content}

## Instructions
- Review the content above
- Make any necessary edits
- Move to 'Approved' folder when ready to post
- Run: python twitter_personal_poster.py to post to Twitter/X

## Character Count
- Current: {len(content)} characters
- Maximum: 280 characters
- Twitter allows up to 280 characters per tweet

## Post Details
- Target: Personal Twitter/X Profile
- Automation: Browser automation (no API key needed)
- Platform: Twitter/X via playwright
"""

    filepath.write_text(draft, encoding='utf-8')
    print(f"Draft created: {filename}")
    print(f"Location: {filepath}")
    print(f"Character count: {len(content)} (Twitter max: 280)")
    print("\nNext steps:")
    print("1. Review the draft in Need_Action folder")
    print("2. Edit if needed (ensure < 280 characters)")
    print("3. Move to Approved folder when ready")
    print("4. Run: python twitter_personal_poster.py")


def create_gold_tier_twitter_content():
    """Create sample Twitter content based on Gold Tier requirements"""
    content = """🚀 Gold Tier Achievement: Autonomous AI Employee with full cross-domain integration!

Our AI now manages Facebook, Instagram, and Twitter/X with comprehensive audit logging and error recovery. Complete business automation at scale! #AI #Automation #BusinessEfficiency"""

    return content


def create_twitter_integration_content():
    """Create content about Twitter integration"""
    content = """🎯 Twitter/X Integration Complete!

Our autonomous AI employee now posts to Twitter/X using browser automation, no API key required! Seamless integration with personal profiles. #Twitter #AI #Automation"""

    return content


def create_odoo_integration_content():
    """Create content about Odoo integration"""
    content = """📊 Odoo Community accounting system integration live!

Self-hosted accounting with JSON-RPC API integration. Complete financial automation and reporting. #Odoo #Accounting #Automation"""

    return content


def create_audit_summary_content():
    """Create content about audit summaries"""
    content = """📋 Weekly Business Audit and CEO Briefing generation now automated!

AI employee provides comprehensive summaries, error recovery, and graceful degradation for maximum reliability. #BusinessAudit #AI #Automation"""

    return content


def list_content_types():
    """List available content types for --help flag"""
    print("Available content types:")
    print("  --gold-tier:          Autonomous AI employee with cross-domain integration")
    print("  --twitter-integration: Twitter/X integration features")
    print("  --odoo-integration:    Odoo accounting system integration")
    print("  --audit-summary:       Business audit and CEO briefing automation")
    print("  --all:               Generate all content types")
    print("\nExample: python create_twitter_draft.py --gold-tier")


def create_all_content():
    """Create all content types"""
    contents = [
        (create_gold_tier_twitter_content(), "Gold Tier: Autonomous AI Employee"),
        (create_twitter_integration_content(), "Twitter/X Integration"),
        (create_odoo_integration_content(), "Odoo Integration"),
        (create_audit_summary_content(), "Business Audit & CEO Briefing")
    ]

    for content, title in contents:
        print(f"\nCreating: {title}")
        create_twitter_draft(content, title)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_twitter_draft.py \"Your tweet content here\"")
        print("Example: python create_twitter_draft.py \"Hello Twitter world!\"")
        print("\nSpecial options:")
        print("  python create_twitter_draft.py --gold-tier    (Gold Tier features)")
        print("  python create_twitter_draft.py --twitter-integration  (Twitter features)")
        print("  python create_twitter_draft.py --odoo-integration     (Odoo features)")
        print("  python create_twitter_draft.py --audit-summary        (Audit features)")
        print("  python create_twitter_draft.py --all         (All content types)")
        print("  python create_twitter_draft.py --help        (Show all options)")
        sys.exit(1)

    content = sys.argv[1]

    # Check if user wants specific content type
    if content == "--gold-tier":
        content = create_gold_tier_twitter_content()
        title = "Gold Tier: Autonomous AI Employee"
        print("Generating Gold Tier Twitter content...")
    elif content == "--twitter-integration":
        content = create_twitter_integration_content()
        title = "Twitter/X Integration"
        print("Generating Twitter integration content...")
    elif content == "--odoo-integration":
        content = create_odoo_integration_content()
        title = "Odoo Integration"
        print("Generating Odoo integration content...")
    elif content == "--audit-summary":
        content = create_audit_summary_content()
        title = "Business Audit & CEO Briefing"
        print("Generating audit & briefing content...")
    elif content == "--all":
        create_all_content()
        sys.exit(0)
    elif content == "--help":
        list_content_types()
        sys.exit(0)
    else:
        title = "Twitter/X Post Draft"

    # Validate character count
    if len(content) > 280:
        print(f"Warning: Tweet is {len(content)} characters (Twitter max: 280)")
        print("Consider shortening your content or it will be automatically truncated.")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            sys.exit(0)

    create_twitter_draft(content, title)