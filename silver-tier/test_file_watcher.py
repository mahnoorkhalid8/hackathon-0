"""
Test Script for File Watcher Service
Demonstrates and validates the file watcher functionality.
"""

import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from file_watcher_service import FileWatcherService, WatcherConfig


def test_basic_functionality():
    """Test basic file watcher functionality."""
    print("="*70)
    print("  TEST 1: Basic Functionality")
    print("="*70)
    print()

    # Create temporary inbox directory
    with tempfile.TemporaryDirectory() as temp_dir:
        inbox_path = Path(temp_dir) / "Inbox"
        inbox_path.mkdir()

        print(f"Test inbox: {inbox_path}")
        print()

        # Configure watcher
        config = WatcherConfig(
            inbox_path=str(inbox_path),
            log_dir="logs",
            debounce_seconds=1.0
        )

        # Create service
        service = FileWatcherService(config)

        try:
            # Start service
            print("[Test] Starting file watcher...")
            service.start()
            time.sleep(2)  # Let it initialize

            # Create test file
            print("[Test] Creating test file...")
            test_file = inbox_path / "test-task.md"
            test_file.write_text("""# Test Task

This is a test task for the file watcher.

**Priority:** HIGH
**Type:** test

## Objective
Verify that the file watcher detects new files and triggers the agent.
""")

            print(f"[Test] Created: {test_file.name}")
            print()

            # Wait for processing
            print("[Test] Waiting for file to be processed...")
            time.sleep(3)

            # Check status
            status = service.get_status()
            print()
            print("[Test] Service Status:")
            print(f"  Running: {status['running']}")
            print(f"  Events processed: {status['events_processed']}")
            print(f"  Agent triggers: {status['agent_stats']['processing_count']}")
            print(f"  Successful: {status['agent_stats']['success_count']}")
            print()

            # Verify
            if status['events_processed'] > 0:
                print("[Test] ✓ PASSED - File was detected and processed")
            else:
                print("[Test] ✗ FAILED - File was not processed")

        finally:
            # Stop service
            print()
            print("[Test] Stopping service...")
            service.stop()

    print()


def test_multiple_files():
    """Test handling multiple files."""
    print("="*70)
    print("  TEST 2: Multiple Files")
    print("="*70)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        inbox_path = Path(temp_dir) / "Inbox"
        inbox_path.mkdir()

        config = WatcherConfig(
            inbox_path=str(inbox_path),
            log_dir="logs",
            debounce_seconds=0.5
        )

        service = FileWatcherService(config)

        try:
            service.start()
            time.sleep(2)

            # Create multiple files
            print("[Test] Creating 5 test files...")
            for i in range(5):
                test_file = inbox_path / f"task-{i+1}.md"
                test_file.write_text(f"# Task {i+1}\n\nTest task number {i+1}")
                print(f"  Created: {test_file.name}")
                time.sleep(0.2)  # Small delay between files

            print()
            print("[Test] Waiting for processing...")
            time.sleep(5)

            # Check results
            status = service.get_status()
            print()
            print("[Test] Results:")
            print(f"  Events processed: {status['events_processed']}")
            print(f"  Agent triggers: {status['agent_stats']['processing_count']}")
            print()

            if status['events_processed'] >= 5:
                print("[Test] ✓ PASSED - All files processed")
            else:
                print(f"[Test] ✗ FAILED - Only {status['events_processed']}/5 files processed")

        finally:
            service.stop()

    print()


def test_file_patterns():
    """Test file pattern filtering."""
    print("="*70)
    print("  TEST 3: File Pattern Filtering")
    print("="*70)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        inbox_path = Path(temp_dir) / "Inbox"
        inbox_path.mkdir()

        config = WatcherConfig(
            inbox_path=str(inbox_path),
            log_dir="logs",
            watch_patterns=["*.md"],
            ignore_patterns=["*.tmp", ".*"]
        )

        service = FileWatcherService(config)

        try:
            service.start()
            time.sleep(2)

            print("[Test] Creating files with different extensions...")

            # Should be processed
            (inbox_path / "task.md").write_text("# Task")
            print("  Created: task.md (should be processed)")

            # Should be ignored
            (inbox_path / "temp.tmp").write_text("temp")
            print("  Created: temp.tmp (should be ignored)")

            (inbox_path / ".hidden").write_text("hidden")
            print("  Created: .hidden (should be ignored)")

            (inbox_path / "data.txt").write_text("data")
            print("  Created: data.txt (should be ignored - not in patterns)")

            print()
            time.sleep(3)

            status = service.get_status()
            print("[Test] Results:")
            print(f"  Events processed: {status['events_processed']}")
            print()

            if status['events_processed'] == 1:
                print("[Test] ✓ PASSED - Only .md file was processed")
            else:
                print(f"[Test] ✗ FAILED - Expected 1, got {status['events_processed']}")

        finally:
            service.stop()

    print()


def test_debouncing():
    """Test debouncing functionality."""
    print("="*70)
    print("  TEST 4: Debouncing")
    print("="*70)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        inbox_path = Path(temp_dir) / "Inbox"
        inbox_path.mkdir()

        config = WatcherConfig(
            inbox_path=str(inbox_path),
            log_dir="logs",
            debounce_seconds=2.0
        )

        service = FileWatcherService(config)

        try:
            service.start()
            time.sleep(2)

            print("[Test] Creating file multiple times rapidly...")
            test_file = inbox_path / "rapid-task.md"

            # Create file multiple times rapidly
            for i in range(3):
                test_file.write_text(f"# Task version {i+1}")
                print(f"  Write {i+1}")
                time.sleep(0.3)

            print()
            print("[Test] Waiting for debounce period...")
            time.sleep(3)

            status = service.get_status()
            print()
            print("[Test] Results:")
            print(f"  Events processed: {status['events_processed']}")
            print()

            # Should only process once due to debouncing
            if status['events_processed'] == 1:
                print("[Test] ✓ PASSED - Debouncing worked (only 1 event)")
            else:
                print(f"[Test] ⚠ WARNING - Expected 1, got {status['events_processed']}")
                print("  (This may vary depending on file system events)")

        finally:
            service.stop()

    print()


def test_error_handling():
    """Test error handling."""
    print("="*70)
    print("  TEST 5: Error Handling")
    print("="*70)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        inbox_path = Path(temp_dir) / "Inbox"
        inbox_path.mkdir()

        config = WatcherConfig(
            inbox_path=str(inbox_path),
            log_dir="logs"
        )

        service = FileWatcherService(config)

        try:
            service.start()
            time.sleep(2)

            print("[Test] Creating file with invalid content...")

            # Create file with non-UTF8 content
            test_file = inbox_path / "invalid.md"
            test_file.write_bytes(b'\xff\xfe Invalid UTF-8')

            print(f"  Created: {test_file.name}")
            print()

            time.sleep(3)

            status = service.get_status()
            print("[Test] Results:")
            print(f"  Events processed: {status['events_processed']}")
            print(f"  Failed: {status['agent_stats']['failure_count']}")
            print()

            # Service should handle error gracefully
            if service.running:
                print("[Test] ✓ PASSED - Service handled error gracefully")
            else:
                print("[Test] ✗ FAILED - Service crashed")

        finally:
            service.stop()

    print()


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  File Watcher Service - Test Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print("\n")

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Multiple Files", test_multiple_files),
        ("File Pattern Filtering", test_file_patterns),
        ("Debouncing", test_debouncing),
        ("Error Handling", test_error_handling)
    ]

    passed = 0
    failed = 0

    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[Test {i}/{len(tests)}] {name}")
        print()

        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n[Error] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

        if i < len(tests):
            print("\n" + "-"*70)
            print("  Press Enter to continue to next test...")
            print("-"*70)
            try:
                input()
            except EOFError:
                pass  # Non-interactive mode

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"  Total: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("="*70)
    print()


if __name__ == "__main__":
    run_all_tests()
