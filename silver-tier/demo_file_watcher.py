"""
Quick Demo - File Watcher Service
Demonstrates the file watcher in action with a simple example.
"""

import sys
import time
import threading
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from file_watcher_service import FileWatcherService, WatcherConfig


def create_demo_files(inbox_path: Path, delay: float = 2.0):
    """
    Create demo files in the inbox directory.

    Args:
        inbox_path: Path to inbox directory
        delay: Delay between file creations
    """
    print("\n[Demo] Starting file creation thread...")
    time.sleep(3)  # Wait for service to start

    demo_files = [
        {
            'name': 'task-1-data-analysis.md',
            'content': '''# Task: Analyze Sales Data

Analyze last quarter's sales data and generate insights.

**Priority:** HIGH
**Type:** data_analysis

## Objective
Generate comprehensive analysis of Q4 2025 sales performance.

## Requirements
- Load sales data from database
- Calculate key metrics
- Identify trends
- Generate visualizations
'''
        },
        {
            'name': 'task-2-report-generation.md',
            'content': '''# Task: Generate Weekly Report

Create weekly status report for stakeholders.

**Priority:** MEDIUM
**Type:** report_generation

## Objective
Summarize this week's activities and progress.

## Sections Required
- Executive summary
- Key achievements
- Challenges
- Next week's plan
'''
        },
        {
            'name': 'task-3-customer-feedback.md',
            'content': '''# Task: Process Customer Feedback

Analyze customer feedback from support tickets.

**Priority:** LOW
**Type:** analysis

## Objective
Extract insights from customer feedback to improve product.

## Data Source
- Support tickets (last 30 days)
- Survey responses
- Social media mentions
'''
        }
    ]

    for i, file_info in enumerate(demo_files, 1):
        print(f"\n[Demo] Creating file {i}/{len(demo_files)}: {file_info['name']}")

        file_path = inbox_path / file_info['name']
        file_path.write_text(file_info['content'], encoding='utf-8')

        print(f"[Demo] ✓ Created: {file_info['name']}")

        if i < len(demo_files):
            print(f"[Demo] Waiting {delay}s before next file...")
            time.sleep(delay)

    print("\n[Demo] All demo files created!")


def main():
    """Run the demo."""
    print("="*70)
    print("  File Watcher Service - Quick Demo")
    print("="*70)
    print()
    print("This demo will:")
    print("  1. Start the file watcher service")
    print("  2. Create 3 demo task files in vault/Inbox/")
    print("  3. Show the service detecting and processing them")
    print("  4. Display statistics")
    print()

    # Ensure inbox exists
    inbox_path = Path("vault/Inbox")
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Configure service
    config = WatcherConfig(
        inbox_path=str(inbox_path),
        log_dir="logs",
        debounce_seconds=1.0,
        log_level="INFO"
    )

    # Create service
    service = FileWatcherService(config)

    try:
        # Start service
        print("[Demo] Starting file watcher service...")
        print()
        service.start()

        # Start file creation thread
        creator_thread = threading.Thread(
            target=create_demo_files,
            args=(inbox_path, 3.0),
            daemon=True
        )
        creator_thread.start()

        # Monitor for 15 seconds
        print("[Demo] Monitoring for 15 seconds...")
        print("[Demo] Watch the console for file detection events...")
        print()

        for i in range(15):
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                status = service.get_status()
                print(f"\n[Demo] Status update: {status['events_processed']} files processed so far")

        # Wait a bit more for processing to complete
        print("\n[Demo] Waiting for processing to complete...")
        time.sleep(5)

        # Show final statistics
        print("\n" + "="*70)
        print("  DEMO RESULTS")
        print("="*70)

        status = service.get_status()
        print(f"\nService Status:")
        print(f"  Running: {status['running']}")
        print(f"  Uptime: {status['uptime']}")
        print(f"  Events processed: {status['events_processed']}")
        print(f"  Queue size: {status['queue_size']}")

        print(f"\nAgent Statistics:")
        print(f"  Total triggers: {status['agent_stats']['processing_count']}")
        print(f"  Successful: {status['agent_stats']['success_count']}")
        print(f"  Failed: {status['agent_stats']['failure_count']}")

        print(f"\nGenerated Files:")
        print(f"  Check vault/Inbox/ for demo files")
        print(f"  Check logs/file_watcher.log for detailed logs")
        print(f"  Check memory/plans/ for generated plans")

        print("\n" + "="*70)
        print("  Demo Complete!")
        print("="*70)
        print()
        print("The file watcher service is still running.")
        print("You can:")
        print("  - Create more files in vault/Inbox/ to test")
        print("  - Press Ctrl+C to stop the service")
        print()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[Demo] Stopping service...")
        service.stop()
        print("[Demo] Demo ended.")
    except Exception as e:
        print(f"\n[Demo] Error: {e}")
        service.stop()
        raise


if __name__ == "__main__":
    main()
