"""
Time Watcher Module
Monitors scheduled tasks and triggers at specified times.
"""

import time
import yaml
from pathlib import Path
from typing import Dict, Callable, List
from datetime import datetime, timedelta
from threading import Thread, Event


class TimeWatcher:
    """Watches for scheduled task triggers."""

    def __init__(self, config: Dict, event_callback: Callable):
        self.config = config
        self.event_callback = event_callback
        self.running = False
        self.stop_event = Event()
        self.thread = None
        self.schedule = []

    def start(self):
        """Start time watcher."""
        if not self.config.get('enabled', False):
            print("[TimeWatcher] Disabled in config")
            return

        # Load schedule
        schedule_file = self.config.get('schedule_file')
        if schedule_file:
            self._load_schedule(schedule_file)

        # Start monitoring thread
        self.running = True
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("[TimeWatcher] Started")

    def stop(self):
        """Stop time watcher."""
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
        print("[TimeWatcher] Stopped")

    def _load_schedule(self, schedule_file: str):
        """Load schedule from YAML file."""
        path = Path(schedule_file)
        if not path.exists():
            print(f"[TimeWatcher] Schedule file not found: {schedule_file}")
            return

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                self.schedule = data.get('scheduled_tasks', [])
                print(f"[TimeWatcher] Loaded {len(self.schedule)} scheduled tasks")
        except Exception as e:
            print(f"[TimeWatcher] Error loading schedule: {e}")

    def _monitor_loop(self):
        """Main monitoring loop."""
        check_interval = self.config.get('check_interval', 60)

        while self.running and not self.stop_event.is_set():
            try:
                self._check_schedule()
            except Exception as e:
                print(f"[TimeWatcher] Error in monitor loop: {e}")

            # Wait for next check
            self.stop_event.wait(check_interval)

    def _check_schedule(self):
        """Check if any scheduled tasks are due."""
        now = datetime.now()

        for task in self.schedule:
            if self._is_task_due(task, now):
                self._trigger_task(task)

    def _is_task_due(self, task: Dict, now: datetime) -> bool:
        """Check if a task is due to run."""
        # Simple time-based checking
        schedule_type = task.get('type', 'cron')

        if schedule_type == 'interval':
            # Check interval-based tasks
            interval_minutes = task.get('interval_minutes', 60)
            last_run = task.get('last_run')

            if not last_run:
                return True

            last_run_time = datetime.fromisoformat(last_run)
            next_run = last_run_time + timedelta(minutes=interval_minutes)

            return now >= next_run

        elif schedule_type == 'daily':
            # Check daily tasks
            target_time = task.get('time', '09:00')
            hour, minute = map(int, target_time.split(':'))

            # Check if current time matches and hasn't run today
            if now.hour == hour and now.minute == minute:
                last_run = task.get('last_run')
                if not last_run:
                    return True

                last_run_date = datetime.fromisoformat(last_run).date()
                return now.date() > last_run_date

        return False

    def _trigger_task(self, task: Dict):
        """Trigger a scheduled task."""
        # Update last run time
        task['last_run'] = datetime.now().isoformat()

        # Create event
        event = {
            'type': task.get('event_type', 'scheduled_task'),
            'source': 'time_watcher',
            'timestamp': datetime.now().isoformat(),
            'payload': {
                'task_name': task.get('name', 'unknown'),
                'task_id': task.get('id', 'unknown'),
                'schedule_type': task.get('type', 'unknown'),
                'parameters': task.get('parameters', {})
            }
        }

        print(f"[TimeWatcher] Triggering task: {task.get('name')}")
        self.event_callback(event)

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self.running
