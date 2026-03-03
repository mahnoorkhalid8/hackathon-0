#!/usr/bin/env python3
"""
Digital FTE Status - Quick Status Check
Shows only recent changes and current state.

Usage:
    python status.py
"""

import os
from pathlib import Path
from datetime import datetime

# Configuration
VAULT_ROOT = Path("AI_Employee_Vault")
INBOX_PATH = VAULT_ROOT / "Inbox"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"
DONE_PATH = VAULT_ROOT / "Done"

def count_files(folder_path):
    """Count markdown files in a folder and return count + filenames."""
    try:
        files = [f.name for f in folder_path.glob("*.md") if f.is_file()]
        return len(files), files
    except:
        return 0, []

def main():
    """Quick status check."""
    print("\n" + "="*50)
    print("  Digital FTE - Quick Status")
    print("="*50)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Count files
    inbox_count, inbox_files = count_files(INBOX_PATH)
    needs_action_count, needs_action_files = count_files(NEEDS_ACTION_PATH)
    done_count, done_files = count_files(DONE_PATH)

    # Show Inbox
    print(f"  Inbox: {inbox_count} file(s)")
    if inbox_files:
        for f in inbox_files:
            print(f"    - {f}")

    # Show Needs_Action
    print(f"\n  Needs_Action: {needs_action_count} file(s)")
    if needs_action_files:
        for f in needs_action_files:
            print(f"    - {f}")

    # Show Done
    print(f"\n  Done: {done_count} file(s)")
    if done_files:
        # Show last 3 files
        for f in sorted(done_files)[-3:]:
            print(f"    - {f}")

    print(f"\n  Total: {inbox_count + needs_action_count + done_count} file(s)")

    # Status
    print("\n" + "-"*50)
    if inbox_count > 0:
        print(f"  [!] {inbox_count} task(s) need triage")
    if needs_action_count > 0:
        print(f"  [!] {needs_action_count} task(s) ready to process")
    if inbox_count == 0 and needs_action_count == 0:
        print("  [OK] All caught up!")

    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
