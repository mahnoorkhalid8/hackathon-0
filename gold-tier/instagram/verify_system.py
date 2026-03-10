#!/usr/bin/env python
"""
Final System Verification
Runs all tests and verifies system integrity
"""

import sys
import subprocess
from pathlib import Path


def run_test(test_file, description):
    """Run a test file and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def verify_files():
    """Verify all required files exist"""
    print(f"\n{'='*60}")
    print("Verifying File Structure")
    print(f"{'='*60}")

    required_files = [
        # Core modules
        "instagram_auth.py",
        "social_media_server.py",
        "ig_workflow_manager.py",
        "error_recovery.py",

        # Tools
        "cli.py",
        "public_server.py",
        "workflow_helper.py",

        # Tests
        "test_instagram.py",
        "test_workflow.py",
        "test_error_recovery.py",

        # Documentation
        "README.md",
        "WORKFLOW.md",
        "ERROR_RECOVERY.md",
        "QUICKSTART.md",
        "COMPLETE.md",
        "FINAL_DELIVERY.md",

        # Config
        "requirements.txt",
        ".gitignore",
        ".env.example",

        # Scripts
        "start.bat",
        "start.sh",

        # Examples
        "examples.py",
        "demo.py"
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  [MISSING] {file}")
        else:
            print(f"  [OK] {file}")

    if missing:
        print(f"\n[FAIL] {len(missing)} files missing")
        return False
    else:
        print(f"\n[PASS] All {len(required_files)} files present")
        return True


def main():
    """Run complete system verification"""
    print("="*60)
    print("Instagram Business Automation - System Verification")
    print("="*60)

    results = {}

    # Verify files
    results["File Structure"] = verify_files()

    # Run tests
    results["API Tests"] = run_test("test_instagram.py", "API Tests")
    results["Workflow Tests"] = run_test("test_workflow.py", "Workflow Tests")
    results["Error Recovery Tests"] = run_test("test_error_recovery.py", "Error Recovery Tests")

    # Summary
    print(f"\n{'='*60}")
    print("Verification Summary")
    print(f"{'='*60}")

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n" + "="*60)
        print("[SUCCESS] SYSTEM VERIFICATION COMPLETE")
        print("="*60)
        print("\nYour Instagram Business automation system is ready!")
        print("\nNext steps:")
        print("  1. Start public server: python public_server.py")
        print("  2. Start workflow manager: python ig_workflow_manager.py")
        print("  3. Create your first post in workflow/Drafts/")
        print("\nOr use the quick start:")
        print("  start.bat  (Windows)")
        print("  ./start.sh (Linux/Mac)")
        return 0
    else:
        print("\n[FAIL] Some verifications failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
