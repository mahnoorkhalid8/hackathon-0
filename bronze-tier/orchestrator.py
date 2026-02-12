#!/usr/bin/env python3
"""
Digital FTE Orchestrator
Performs a one-time check of the system state and processes pending tasks.

Usage:
    python orchestrator.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Configuration
VAULT_ROOT = Path("AI_Employee_Vault")
INBOX_PATH = VAULT_ROOT / "Inbox"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"
DONE_PATH = VAULT_ROOT / "Done"
DASHBOARD_PATH = VAULT_ROOT / "Dashboard.md"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a header with formatting."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_section(text):
    """Print a section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}>> {text}{Colors.END}")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}  [OK] {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}  [!] {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}  [X] {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}  [i] {text}{Colors.END}")

def count_markdown_files(folder_path):
    """Count markdown files in a folder."""
    try:
        files = [f for f in folder_path.glob("*.md") if f.is_file()]
        return len(files), files
    except Exception as e:
        print_error(f"Error reading {folder_path.name}: {e}")
        return 0, []

def check_system_health():
    """Check if all required directories and files exist."""
    print_section("System Health Check")

    all_good = True

    # Check directories
    required_dirs = [VAULT_ROOT, INBOX_PATH, NEEDS_ACTION_PATH, DONE_PATH]
    for directory in required_dirs:
        if directory.exists():
            print_success(f"{directory.name}/ exists")
        else:
            print_error(f"{directory.name}/ NOT FOUND")
            all_good = False

    # Check Dashboard
    if DASHBOARD_PATH.exists():
        print_success("Dashboard.md exists")
    else:
        print_error("Dashboard.md NOT FOUND")
        all_good = False

    # Check Python dependencies
    try:
        import watchdog
        import yaml
        print_success("Python dependencies installed")
    except ImportError as e:
        print_warning(f"Missing Python dependency: {e}")

    # Check Claude CLI
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Claude CLI available: {result.stdout.strip()}")
        else:
            print_warning("Claude CLI not responding correctly")
    except FileNotFoundError:
        print_warning("Claude CLI not found (optional for manual mode)")
    except Exception as e:
        print_warning(f"Claude CLI check failed: {e}")

    return all_good

def analyze_folders():
    """Analyze current state of all folders."""
    print_section("Folder Analysis")

    # Inbox
    inbox_count, inbox_files = count_markdown_files(INBOX_PATH)
    print_info(f"Inbox: {inbox_count} file(s)")
    for file in inbox_files:
        prefix = ""
        if file.name.startswith("[CLARIFICATION]"):
            prefix = f"{Colors.YELLOW}[NEEDS CLARIFICATION]{Colors.END} "
        elif file.name.startswith("[BLOCKED]"):
            prefix = f"{Colors.RED}[BLOCKED]{Colors.END} "
        print(f"    - {prefix}{file.name}")

    # Needs Action
    needs_action_count, needs_action_files = count_markdown_files(NEEDS_ACTION_PATH)
    print_info(f"Needs_Action: {needs_action_count} file(s)")
    for file in needs_action_files:
        print(f"    - {file.name}")

    # Done
    done_count, done_files = count_markdown_files(DONE_PATH)
    print_info(f"Done: {done_count} file(s)")
    if done_count > 0:
        print(f"    - Showing last 5:")
        for file in sorted(done_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"      • {file.name}")

    return {
        'inbox': inbox_count,
        'needs_action': needs_action_count,
        'done': done_count,
        'inbox_files': inbox_files,
        'needs_action_files': needs_action_files
    }

def check_pending_tasks(state):
    """Check for tasks that need attention."""
    print_section("Pending Tasks")

    pending_count = 0

    # Check for untriaged tasks in Inbox
    untriaged = [f for f in state['inbox_files']
                 if not f.name.startswith('[CLARIFICATION]')
                 and not f.name.startswith('[BLOCKED]')]

    if untriaged:
        print_warning(f"{len(untriaged)} task(s) awaiting triage in Inbox")
        for file in untriaged:
            print(f"    - {file.name}")
        pending_count += len(untriaged)
    else:
        print_success("No tasks awaiting triage")

    # Check for tasks needing clarification
    clarification = [f for f in state['inbox_files']
                     if f.name.startswith('[CLARIFICATION]')]

    if clarification:
        print_warning(f"{len(clarification)} task(s) need clarification")
        for file in clarification:
            print(f"    - {file.name}")
        pending_count += len(clarification)

    # Check for blocked tasks
    blocked = [f for f in state['inbox_files']
               if f.name.startswith('[BLOCKED]')]

    if blocked:
        print_warning(f"{len(blocked)} task(s) are blocked")
        for file in blocked:
            print(f"    - {file.name}")
        pending_count += len(blocked)

    # Check for tasks in Needs_Action
    if state['needs_action'] > 0:
        print_info(f"{state['needs_action']} task(s) ready for processing")
        for file in state['needs_action_files']:
            print(f"    - {file.name}")
    else:
        print_success("No tasks in Needs_Action queue")

    return pending_count

def show_dashboard_summary():
    """Show summary from Dashboard."""
    print_section("Dashboard Summary")

    try:
        with open(DASHBOARD_PATH, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Extract metrics table
        if "## Current Status" in content:
            lines = content.split('\n')
            for line in lines:
                if '|' in line and 'Metric' not in line and '---' not in line:
                    # Replace Unicode arrows with ASCII
                    line = line.replace('↑', '^').replace('↓', 'v').replace('→', '->')
                    line = line.replace('✓', 'OK')
                    # Encode to ASCII, replacing any remaining Unicode
                    line = line.encode('ascii', errors='replace').decode('ascii')
                    print(f"  {line.strip()}")

        # Show recent activity
        if "## Activity Log" in content:
            print_info("Recent Activity (last 5 entries):")
            lines = content.split('\n')
            activity_lines = []
            in_activity = False
            for line in lines:
                if "## Activity Log" in line:
                    in_activity = True
                    continue
                if in_activity and line.startswith('**'):
                    # Clean line for ASCII output
                    line = line.encode('ascii', errors='replace').decode('ascii')
                    activity_lines.append(line)
                if in_activity and line.startswith('---'):
                    break

            for line in activity_lines[-5:]:
                print(f"    {line}")

    except Exception as e:
        print_warning(f"Dashboard read issue: {str(e)[:50]}")

def suggest_next_actions(state, pending_count):
    """Suggest what to do next."""
    print_section("Suggested Next Actions")

    if pending_count == 0 and state['needs_action'] == 0:
        print_success("All caught up! No pending tasks.")
        print_info("Create a new task in Inbox/ to get started")
        return

    actions = []

    # Untriaged tasks
    untriaged = [f for f in state['inbox_files']
                 if not f.name.startswith('[CLARIFICATION]')
                 and not f.name.startswith('[BLOCKED]')]
    if untriaged:
        actions.append(f"1. Start inbox_watcher.py to auto-triage {len(untriaged)} task(s)")
        actions.append(f"   OR manually triage tasks in Inbox/")

    # Tasks needing clarification
    clarification = [f for f in state['inbox_files']
                     if f.name.startswith('[CLARIFICATION]')]
    if clarification:
        actions.append(f"2. Review and update {len(clarification)} task(s) needing clarification")

    # Blocked tasks
    blocked = [f for f in state['inbox_files']
               if f.name.startswith('[BLOCKED]')]
    if blocked:
        actions.append(f"3. Resolve blockers for {len(blocked)} task(s)")

    # Tasks ready for action
    if state['needs_action'] > 0:
        actions.append(f"4. Process {state['needs_action']} task(s) in Needs_Action/")

    for action in actions:
        print(f"  {action}")

def main():
    """Main orchestrator function."""
    print_header("Digital FTE Orchestrator")
    print(f"{Colors.BOLD}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Step 1: System health check
    health_ok = check_system_health()

    if not health_ok:
        print_error("\nSystem health check failed. Please fix issues before continuing.")
        sys.exit(1)

    # Step 2: Analyze folders
    state = analyze_folders()

    # Step 3: Check pending tasks
    pending_count = check_pending_tasks(state)

    # Step 4: Show dashboard summary
    show_dashboard_summary()

    # Step 5: Suggest next actions
    suggest_next_actions(state, pending_count)

    # Summary
    print_header("Summary")
    print(f"  Total tasks in system: {state['inbox'] + state['needs_action'] + state['done']}")
    print(f"  Pending attention: {pending_count}")
    print(f"  Ready for processing: {state['needs_action']}")
    print(f"  Completed: {state['done']}")

    if pending_count > 0 or state['needs_action'] > 0:
        print(f"\n{Colors.YELLOW}  [!] Action required: {pending_count + state['needs_action']} task(s) need attention{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}  [OK] All systems operational{Colors.END}")

    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Orchestrator interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
