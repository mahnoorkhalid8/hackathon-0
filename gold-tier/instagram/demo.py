#!/usr/bin/env python
"""
Instagram Workflow Demo
Demonstrates the complete workflow from draft to posting
"""

import time
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}\n")


def demo_setup():
    """Demo: Initial setup"""
    print_header("DEMO: Instagram Workflow Setup")

    print("Step 1: Creating folder structure...")
    import subprocess
    result = subprocess.run(
        ["python", "ig_workflow_manager.py", "--setup"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

    print("\n✓ Folder structure created!")


def demo_create_draft():
    """Demo: Create a draft post"""
    print_header("DEMO: Creating a Draft Post")

    # Create a sample caption
    caption = """Beautiful sunset at the beach 🌅

Perfect end to a perfect day. The colors were absolutely stunning!

#sunset #beach #nature #photography #beautiful #instagram #instagood #photooftheday
"""

    drafts = Path("workflow/Drafts")
    drafts.mkdir(parents=True, exist_ok=True)

    # Create sample caption file
    caption_file = drafts / "demo_sunset.txt"
    caption_file.write_text(caption, encoding='utf-8')

    print("Created draft post:")
    print(f"  Caption file: {caption_file}")
    print(f"\nCaption preview:")
    print(f"  {caption[:80]}...")

    print("\n✓ Draft created!")
    print("\nNote: In real usage, you would also have demo_sunset.jpg")
    print("      For this demo, we're just showing the workflow")


def demo_list_drafts():
    """Demo: List drafts"""
    print_header("DEMO: Listing Drafts")

    import subprocess
    result = subprocess.run(
        ["python", "workflow_helper.py", "list"],
        capture_output=True,
        text=True
    )
    print(result.stdout)


def demo_approve():
    """Demo: Approve a post"""
    print_header("DEMO: Approving a Post")

    print("When you're ready to post, move files to Approved/:")
    print("  python workflow_helper.py approve demo_sunset.jpg")
    print("\nOr manually:")
    print("  mv workflow/Drafts/demo_sunset.* workflow/Approved/")

    print("\n✓ Once approved, the workflow manager will:")
    print("  1. Copy image to Public/ folder")
    print("  2. Generate public URL")
    print("  3. Post to Instagram via MCP server")
    print("  4. Move to Done/ folder with timestamp")


def demo_monitoring():
    """Demo: Show monitoring"""
    print_header("DEMO: Workflow Monitoring")

    print("Start the workflow manager:")
    print("  python ig_workflow_manager.py")
    print("\nIt will:")
    print("  ✓ Monitor workflow/Approved/ folder")
    print("  ✓ Auto-process new images")
    print("  ✓ Log all operations")
    print("  ✓ Move completed posts to Done/")

    print("\nExample output:")
    print("""
============================================================
Processing: demo_sunset.jpg
============================================================
  Caption: Beautiful sunset at the beach 🌅...
  Copying to Public folder...
  Public URL: http://localhost:8000/demo_sunset.jpg
  Posting to Instagram...
  ✓ Posted successfully!
  Post ID: 18123456789012345
  ✓ Moved to Done: workflow/Done/20260305_160000
""")


def demo_public_server():
    """Demo: Public server setup"""
    print_header("DEMO: Public Image Server")

    print("Instagram needs public URLs to fetch images.")
    print("\nOption 1: Local testing")
    print("  python public_server.py")
    print("  URL: http://localhost:8000")

    print("\nOption 2: Public access (production)")
    print("  1. Install ngrok: https://ngrok.com/download")
    print("  2. Run: ngrok http 8000")
    print("  3. Copy the public URL (e.g., https://abc123.ngrok.io)")
    print("  4. Update workflow_config.json:")
    print('     {"public_url_base": "https://abc123.ngrok.io"}')


def demo_complete_workflow():
    """Demo: Complete workflow"""
    print_header("DEMO: Complete Workflow")

    print("Complete workflow in action:")
    print("\n1. CREATE DRAFT")
    print("   - Add image to workflow/Drafts/")
    print("   - Create caption file (same name, .txt extension)")

    print("\n2. REVIEW & APPROVE")
    print("   - Review your post")
    print("   - Move to workflow/Approved/")

    print("\n3. AUTOMATIC POSTING")
    print("   - Workflow manager detects new file")
    print("   - Copies to Public/ folder")
    print("   - Posts to Instagram")
    print("   - Moves to Done/ folder")

    print("\n4. VERIFICATION")
    print("   - Check logs/workflow_logs.json")
    print("   - View post on Instagram")
    print("   - Files archived in Done/")


def demo_integration():
    """Demo: Integration with autonomous employee"""
    print_header("DEMO: Autonomous Employee Integration")

    print("Integration points:")

    print("\n1. EMAIL TRIGGER")
    print("   - Email handler receives image attachment")
    print("   - Saves to workflow/Drafts/")
    print("   - AI generates caption")

    print("\n2. AI CAPTION GENERATION")
    print("   - Analyze image content")
    print("   - Generate engaging caption")
    print("   - Add relevant hashtags")
    print("   - Save as .txt file")

    print("\n3. APPROVAL WORKFLOW")
    print("   - Human reviews draft")
    print("   - Or AI auto-approves based on rules")
    print("   - Moves to Approved/")

    print("\n4. AUTOMATED POSTING")
    print("   - Workflow manager handles posting")
    print("   - Logs all operations")
    print("   - Archives completed posts")

    print("\n5. MONITORING & ANALYTICS")
    print("   - Track post performance")
    print("   - Get insights via MCP server")
    print("   - Generate reports")


def main():
    """Run complete demo"""
    print("\n" + "="*60)
    print("INSTAGRAM WORKFLOW MANAGER - COMPLETE DEMO")
    print("="*60)

    demos = [
        ("Setup", demo_setup),
        ("Create Draft", demo_create_draft),
        ("List Drafts", demo_list_drafts),
        ("Approve Post", demo_approve),
        ("Monitoring", demo_monitoring),
        ("Public Server", demo_public_server),
        ("Complete Workflow", demo_complete_workflow),
        ("Integration", demo_integration)
    ]

    for i, (name, func) in enumerate(demos, 1):
        try:
            func()
            if i < len(demos):
                input("\nPress Enter to continue to next demo...")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted.")
            break
        except Exception as e:
            print(f"\nError in demo: {e}")

    print_header("DEMO COMPLETE")
    print("Your Instagram workflow system is ready!")
    print("\nNext steps:")
    print("  1. Start public server: python public_server.py")
    print("  2. Start workflow manager: python ig_workflow_manager.py")
    print("  3. Create your first post in workflow/Drafts/")
    print("  4. Approve and watch it post automatically!")
    print("\nDocumentation:")
    print("  - WORKFLOW.md - Complete workflow guide")
    print("  - README.md - API documentation")
    print("  - QUICKSTART.md - 5-minute setup")


if __name__ == "__main__":
    main()
