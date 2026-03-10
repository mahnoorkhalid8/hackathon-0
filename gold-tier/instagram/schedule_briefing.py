#!/usr/bin/env python
"""
Automated CEO Briefing Scheduler
Generates and emails weekly Instagram performance reports
"""

import sys
import schedule
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ceo_briefing import generate_ceo_briefing


def send_briefing_email(report: str, recipient: str):
    """
    Send briefing via email (placeholder for email integration)

    Args:
        report: Markdown report content
        recipient: Email address
    """
    # TODO: Integrate with email system
    # For now, just save to file
    print(f"Would send email to: {recipient}")
    print("Email integration not yet implemented")


def generate_and_send_briefing():
    """Generate briefing and send/save it"""
    print(f"\n{'='*60}")
    print(f"Generating CEO Briefing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    result = generate_ceo_briefing(days=7, save=True)

    if result["success"]:
        print(f"✓ Report generated successfully")
        print(f"✓ Saved to: {result.get('saved_to', 'N/A')}")

        # Optional: Send email
        # send_briefing_email(result["report"], "ceo@company.com")
    else:
        print(f"✗ Error generating report: {result['error']}")


def run_scheduler():
    """Run the scheduler"""
    print("CEO Briefing Scheduler Started")
    print("="*60)
    print("Schedule: Every Monday at 8:00 AM")
    print("Press Ctrl+C to stop")
    print("="*60)

    # Schedule for every Monday at 8:00 AM
    schedule.every().monday.at("08:00").do(generate_and_send_briefing)

    # For testing: Generate immediately
    print("\nGenerating initial briefing...")
    generate_and_send_briefing()

    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CEO Briefing Scheduler")
    parser.add_argument("--now", action="store_true", help="Generate briefing immediately and exit")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")

    args = parser.parse_args()

    if args.now:
        # Generate immediately
        result = generate_ceo_briefing(days=args.days, save=True)
        if result["success"]:
            print(result["report"])
            print(f"\n✓ Report saved to: {result.get('saved_to', 'N/A')}")
            sys.exit(0)
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)
    else:
        # Run scheduler
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print("\n\nScheduler stopped.")
