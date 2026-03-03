"""
Test Script for Scheduler System

Tests the scheduler components and validates the setup.

Usage:
    python test_scheduler.py

Author: Digital FTE System
Date: 2026-02-13
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_test(name, passed):
    """Print test result."""
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} {name}")


def test_python_installation():
    """Test Python installation."""
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version = result.stdout.strip() or result.stderr.strip()
        print(f"  Python version: {version}")
        return result.returncode == 0
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_run_agent_exists():
    """Test if run_agent.py exists."""
    exists = Path("run_agent.py").exists()
    if exists:
        print("  Found: run_agent.py")
    else:
        print("  Missing: run_agent.py")
    return exists


def test_scheduler_files():
    """Test if scheduler files exist."""
    files = [
        "scheduler/windows/run_watchers.xml",
        "scheduler/windows/ceo_report.xml",
        "scheduler/windows/setup_scheduler.ps1",
        "scheduler/cron/crontab.txt",
        "scheduler/cron/setup_scheduler.sh",
        "scheduler/README.md"
    ]

    all_exist = True
    for file in files:
        exists = Path(file).exists()
        status = "[OK]" if exists else "[MISS]"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False

    return all_exist


def test_logs_directory():
    """Test if logs directory exists."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print("  Created: logs/")
    else:
        print("  Exists: logs/")
    return logs_dir.exists()


def test_memory_directories():
    """Test if memory directories exist."""
    dirs = [
        "memory/Inbox",
        "memory/Needs_Action",
        "memory/Needs_Approval",
        "memory/Done",
        "memory/reports"
    ]

    all_exist = True
    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}/")
        else:
            print(f"  Exists: {dir_path}/")

    return all_exist


def test_run_agent_help():
    """Test run_agent.py help command."""
    try:
        result = subprocess.run(
            ["python", "run_agent.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("  run_agent.py --help works")
            return True
        else:
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_windows_scheduler():
    """Test Windows Task Scheduler setup (Windows only)."""
    if sys.platform != "win32":
        print("  Skipped: Not Windows")
        return True

    try:
        # Check if tasks exist
        result = subprocess.run(
            ["powershell", "-Command", "Get-ScheduledTask -TaskPath '\\DigitalFTE\\*' -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if "RunWatchers" in result.stdout or "CEOReport" in result.stdout:
            print("  Found scheduled tasks in \\DigitalFTE\\")
            return True
        else:
            print("  No scheduled tasks found (run setup_scheduler.ps1)")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_cron_setup():
    """Test cron setup (Linux/macOS only)."""
    if sys.platform == "win32":
        print("  Skipped: Not Linux/macOS")
        return True

    try:
        # Check if cron jobs exist
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if "run_agent.py" in result.stdout:
            print("  Found cron jobs for run_agent.py")
            return True
        else:
            print("  No cron jobs found (run setup_scheduler.sh)")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_dry_run():
    """Test dry run of watchers command."""
    print("  Running: python run_agent.py watchers")
    print("  (This may take a few seconds...)")

    try:
        result = subprocess.run(
            ["python", "run_agent.py", "watchers"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("  Command executed successfully")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            print("  Output (last 5 lines):")
            for line in lines[-5:]:
                print(f"    {line}")
            return True
        else:
            print(f"  Command failed with exit code {result.returncode}")
            print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("  Command timed out (may still be running)")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    """Run all tests."""
    print_header("Scheduler System Test Suite")

    results = {}

    # Test 1: Python installation
    print("[1/9] Testing Python installation...")
    results["python"] = test_python_installation()

    # Test 2: run_agent.py exists
    print("\n[2/9] Testing run_agent.py exists...")
    results["run_agent"] = test_run_agent_exists()

    # Test 3: Scheduler files exist
    print("\n[3/9] Testing scheduler files...")
    results["scheduler_files"] = test_scheduler_files()

    # Test 4: Logs directory
    print("\n[4/9] Testing logs directory...")
    results["logs"] = test_logs_directory()

    # Test 5: Memory directories
    print("\n[5/9] Testing memory directories...")
    results["memory"] = test_memory_directories()

    # Test 6: run_agent.py help
    print("\n[6/9] Testing run_agent.py help...")
    results["help"] = test_run_agent_help()

    # Test 7: Windows scheduler (Windows only)
    print("\n[7/9] Testing Windows Task Scheduler...")
    results["windows"] = test_windows_scheduler()

    # Test 8: Cron setup (Linux/macOS only)
    print("\n[8/9] Testing cron setup...")
    results["cron"] = test_cron_setup()

    # Test 9: Dry run
    print("\n[9/9] Testing dry run...")
    results["dry_run"] = test_dry_run()

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        print_test(name, result)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
