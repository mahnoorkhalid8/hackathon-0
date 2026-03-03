#!/usr/bin/env python3
"""
Facebook Watcher Service

This script runs the Facebook watcher as part of the overall AI employee system.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
import threading

def run_facebook_watcher():
    """Run the Facebook watcher in a subprocess."""
    print("Starting Facebook Watcher Service...")

    # Change to the project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    try:
        # Run the Facebook watcher
        process = subprocess.Popen([
            sys.executable,
            str(project_root / "facebook" / "facebook_watcher.py")
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(project_root))

        print(f"Facebook Watcher started with PID: {process.pid}")

        # Monitor the process
        while True:
            if process.poll() is not None:  # Process has terminated
                stdout, stderr = process.communicate()
                print(f"Facebook Watcher terminated with code: {process.returncode}")
                if stdout:
                    print(f"STDOUT: {stdout}")
                if stderr:
                    print(f"STDERR: {stderr}")
                break

            time.sleep(1)  # Check every second

    except KeyboardInterrupt:
        print("Stopping Facebook Watcher...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Facebook Watcher stopped.")

def signal_handler(sig, frame):
    """Handle exit signals gracefully."""
    print('\nReceived interrupt signal. Stopping services...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Facebook Watcher Service Manager")
    print("Press Ctrl+C to stop the service")

    try:
        run_facebook_watcher()
    except KeyboardInterrupt:
        print("\nService stopped by user.")
    except Exception as e:
        print(f"Error running Facebook Watcher: {e}")
        sys.exit(1)