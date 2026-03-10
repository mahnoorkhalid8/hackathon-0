#!/usr/bin/env python
"""
Instagram Workflow Helper
Quick commands for common workflow operations
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


def create_post(image_path: str, caption: str = None):
    """
    Create a new post in Drafts folder

    Args:
        image_path: Path to image file
        caption: Optional caption text
    """
    drafts = Path("workflow/Drafts")
    drafts.mkdir(parents=True, exist_ok=True)

    image_file = Path(image_path)
    if not image_file.exists():
        print(f"Error: Image not found: {image_path}")
        return False

    # Copy image to Drafts
    dest_image = drafts / image_file.name
    shutil.copy2(image_file, dest_image)
    print(f"✓ Image copied to: {dest_image}")

    # Create caption file if provided
    if caption:
        caption_file = dest_image.with_suffix('.txt')
        caption_file.write_text(caption, encoding='utf-8')
        print(f"✓ Caption saved to: {caption_file}")

    print(f"\nNext step: Review and approve")
    print(f"  python workflow_helper.py approve {image_file.name}")

    return True


def approve_post(image_name: str):
    """
    Move post from Drafts to Approved (triggers posting)

    Args:
        image_name: Name of image file in Drafts
    """
    drafts = Path("workflow/Drafts")
    approved = Path("workflow/Approved")
    approved.mkdir(parents=True, exist_ok=True)

    image_file = drafts / image_name
    if not image_file.exists():
        print(f"Error: Image not found in Drafts: {image_name}")
        return False

    # Move image
    dest_image = approved / image_name
    shutil.move(str(image_file), str(dest_image))
    print(f"✓ Moved image to Approved: {dest_image}")

    # Move caption if exists
    caption_file = image_file.with_suffix('.txt')
    if caption_file.exists():
        dest_caption = approved / caption_file.name
        shutil.move(str(caption_file), str(dest_caption))
        print(f"✓ Moved caption to Approved: {dest_caption}")

    print(f"\n✓ Post approved! Workflow manager will process it automatically.")
    print(f"  (Make sure workflow manager is running)")

    return True


def list_drafts():
    """List all posts in Drafts folder"""
    drafts = Path("workflow/Drafts")
    if not drafts.exists():
        print("No Drafts folder found")
        return

    images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        images.extend(drafts.glob(f"*{ext}"))

    if not images:
        print("No drafts found")
        return

    print(f"\nDrafts ({len(images)}):")
    print("=" * 60)

    for image in sorted(images):
        caption_file = image.with_suffix('.txt')
        has_caption = "✓" if caption_file.exists() else "✗"

        print(f"  [{has_caption}] {image.name}")
        if caption_file.exists():
            caption = caption_file.read_text(encoding='utf-8')
            preview = caption[:50] + "..." if len(caption) > 50 else caption
            print(f"      {preview}")

    print("\nTo approve a post:")
    print("  python workflow_helper.py approve <image_name>")


def list_approved():
    """List all posts in Approved folder"""
    approved = Path("workflow/Approved")
    if not approved.exists():
        print("No Approved folder found")
        return

    images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        images.extend(approved.glob(f"*{ext}"))

    if not images:
        print("No approved posts waiting")
        return

    print(f"\nApproved ({len(images)}):")
    print("=" * 60)

    for image in sorted(images):
        print(f"  {image.name}")

    print("\nThese will be posted automatically by workflow manager")


def list_done():
    """List recently posted content"""
    done = Path("workflow/Done")
    if not done.exists():
        print("No Done folder found")
        return

    folders = sorted(done.iterdir(), reverse=True)[:10]  # Last 10

    if not folders:
        print("No completed posts")
        return

    print(f"\nRecently Posted:")
    print("=" * 60)

    for folder in folders:
        if folder.is_dir():
            timestamp = folder.name
            images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
            if images:
                print(f"  [{timestamp}] {images[0].name}")


def show_status():
    """Show workflow status"""
    print("\nInstagram Workflow Status")
    print("=" * 60)

    # Count files in each folder
    folders = {
        "Drafts": Path("workflow/Drafts"),
        "Approved": Path("workflow/Approved"),
        "Public": Path("workflow/Public"),
        "Done": Path("workflow/Done"),
        "Failed": Path("workflow/Failed")
    }

    for name, folder in folders.items():
        if folder.exists():
            images = []
            for ext in ['.jpg', '.jpeg', '.png']:
                images.extend(folder.glob(f"**/*{ext}"))
            count = len(images)
            print(f"  {name:12} {count:3} images")
        else:
            print(f"  {name:12} (not created)")

    print("\nCommands:")
    print("  python workflow_helper.py list          - List drafts")
    print("  python workflow_helper.py approve <img> - Approve a post")
    print("  python workflow_helper.py status        - Show this status")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_status()
        return

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: python workflow_helper.py create <image_path> [caption]")
            return
        image_path = sys.argv[2]
        caption = sys.argv[3] if len(sys.argv) > 3 else None
        create_post(image_path, caption)

    elif command == "approve":
        if len(sys.argv) < 3:
            print("Usage: python workflow_helper.py approve <image_name>")
            return
        approve_post(sys.argv[2])

    elif command == "list":
        list_drafts()

    elif command == "approved":
        list_approved()

    elif command == "done":
        list_done()

    elif command == "status":
        show_status()

    else:
        print(f"Unknown command: {command}")
        print("\nAvailable commands:")
        print("  create <image> [caption] - Create new post in Drafts")
        print("  approve <image>          - Move post to Approved")
        print("  list                     - List drafts")
        print("  approved                 - List approved posts")
        print("  done                     - List recently posted")
        print("  status                   - Show workflow status")


if __name__ == "__main__":
    main()
