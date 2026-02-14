"""
Demo Script - Silver Tier Digital FTE
Demonstrates the system in action with a simulated workflow.
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_workflow():
    """Run a demonstration workflow."""

    print_section("Silver Tier Digital FTE - Demo")

    print("This demo will:")
    print("1. Start the orchestrator")
    print("2. Simulate a file being added to Inbox/")
    print("3. Show the reasoning process")
    print("4. Route the task appropriately")
    print("5. Display the results")

    input("\nPress Enter to start...")

    # Initialize orchestrator
    print_section("Initializing System")
    orchestrator = Orchestrator()

    # Start system
    print_section("Starting Orchestrator")
    orchestrator.start()

    print("System is now running...")
    print("Watchers are monitoring for events...")

    # Wait a moment
    time.sleep(2)

    # Check if demo task exists
    demo_task = Path("./memory/Inbox/demo-task.md")
    if demo_task.exists():
        print(f"\n[Demo] Found demo task: {demo_task}")
        print("[Demo] File watcher should detect this file...")
        print("[Demo] Watch the console for processing events...")
    else:
        print("\n[Demo] No demo task found in Inbox/")
        print("[Demo] You can create a task file in memory/Inbox/ to test")

    # Let it run for a bit
    print("\n[Demo] System running for 30 seconds...")
    print("[Demo] You can:")
    print("  - Check memory/Dashboard.md for status")
    print("  - Check memory/Plan.md for reasoning")
    print("  - Check memory/Needs_Approval/ for tasks requiring review")
    print("  - Check memory/Needs_Action/ for auto-approved tasks")

    try:
        for i in range(30, 0, -5):
            print(f"[Demo] {i} seconds remaining...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[Demo] Interrupted by user")

    # Show status
    print_section("System Status")
    status = orchestrator.get_status()
    print(f"Running: {status['running']}")
    print(f"Queue Size: {status['queue_size']}")
    print(f"Tasks Processed: {status['metrics']['tasks_processed']}")
    print(f"Auto-Approved: {status['metrics']['auto_approved']}")
    print(f"Required Approval: {status['metrics']['required_approval']}")

    # Stop system
    print_section("Shutting Down")
    orchestrator.stop()

    print("\n[Demo] Demo complete!")
    print("\nNext steps:")
    print("1. Review memory/Dashboard.md for system state")
    print("2. Check memory/Plan.md to see reasoning process")
    print("3. Look in memory/Needs_Approval/ for tasks to review")
    print("4. Examine logs/ directory for detailed logs")
    print("\nTo run the system normally: python main.py")


if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print(f"\n[Error] Demo failed: {e}")
        import traceback
        traceback.print_exc()
