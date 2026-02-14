"""
Silver Tier Digital FTE - Main Entry Point
"""

import sys
import signal
import time
from pathlib import Path

from core.orchestrator import Orchestrator


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\n\n[Main] Received shutdown signal")
    if 'orchestrator' in globals():
        orchestrator.stop()
    sys.exit(0)


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Silver Tier Digital FTE v1.0                       ║
║           Local-First Autonomous Assistant                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize orchestrator
    config_path = "./config/fte_config.yaml"

    if not Path(config_path).exists():
        print(f"[Error] Configuration file not found: {config_path}")
        print("[Error] Please ensure config/fte_config.yaml exists")
        sys.exit(1)

    try:
        global orchestrator
        orchestrator = Orchestrator(config_path)

        # Start system
        orchestrator.start()

        # Keep running
        print("[Main] Press Ctrl+C to stop\n")

        while True:
            time.sleep(1)

            # Optional: Print status periodically
            # status = orchestrator.get_status()
            # print(f"[Status] Queue: {status['queue_size']}, Tasks: {status['metrics']['tasks_processed']}")

    except KeyboardInterrupt:
        print("\n[Main] Keyboard interrupt received")
        orchestrator.stop()
    except Exception as e:
        print(f"\n[Error] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
