"""
Main Orchestrator Module
Coordinates all components and manages the execution lifecycle.
"""

import yaml
import queue
import time
from pathlib import Path
from typing import Dict, List
from threading import Thread, Lock
from datetime import datetime

from core.context_loader import ContextLoader
from core.reasoning_engine import ReasoningEngine
from core.task_router import TaskRouter
from core.state_manager import StateManager
from core.executor import Executor
from watchers.file_watcher import FileWatcher
from watchers.time_watcher import TimeWatcher


class Orchestrator:
    """Main orchestration engine for Digital FTE."""

    def __init__(self, config_path: str = "./config/fte_config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.context_loader = ContextLoader(self.config)
        self.reasoning_engine = ReasoningEngine(self.config)
        self.task_router = TaskRouter(self.config)
        self.state_manager = StateManager(self.config)
        self.executor = Executor(self.config)

        # Event queue
        self.event_queue = queue.Queue()
        self.event_lock = Lock()

        # Watchers
        self.watchers = {}
        self._init_watchers()

        # State
        self.running = False
        self.metrics = {
            'tasks_processed': 0,
            'auto_approved': 0,
            'required_approval': 0,
            'mcp_calls': 0,
            'recent_activity': [],
            'alerts': [],
            'next_scheduled': []
        }

    def _init_watchers(self):
        """Initialize all configured watchers."""
        watcher_configs = self.config.get('watchers', {})

        # File watcher
        if watcher_configs.get('file_watcher', {}).get('enabled', False):
            self.watchers['file'] = FileWatcher(
                watcher_configs['file_watcher'],
                self.on_event
            )

        # Time watcher
        if watcher_configs.get('time_watcher', {}).get('enabled', False):
            self.watchers['time'] = TimeWatcher(
                watcher_configs['time_watcher'],
                self.on_event
            )

    def start(self):
        """Start the orchestrator and all watchers."""
        print("\n" + "="*60)
        print("  Silver Tier Digital FTE - Starting")
        print("="*60 + "\n")

        self.running = True

        # Start watchers
        for name, watcher in self.watchers.items():
            try:
                watcher.start()
                self.metrics[f'{name}_watcher_active'] = True
            except Exception as e:
                print(f"[Orchestrator] Failed to start {name} watcher: {e}")
                self.metrics['alerts'].append(f"Failed to start {name} watcher")

        # Start event processing thread
        self.event_thread = Thread(target=self._process_events, daemon=True)
        self.event_thread.start()

        # Start execution thread
        self.execution_thread = Thread(target=self._execute_tasks, daemon=True)
        self.execution_thread.start()

        # Update dashboard
        self.state_manager.update_dashboard(self.metrics)

        print("\n[Orchestrator] System operational")
        print("[Orchestrator] Monitoring for events...\n")

    def stop(self):
        """Stop the orchestrator and all watchers."""
        print("\n[Orchestrator] Shutting down...")

        self.running = False

        # Stop watchers
        for name, watcher in self.watchers.items():
            try:
                watcher.stop()
            except Exception as e:
                print(f"[Orchestrator] Error stopping {name} watcher: {e}")

        # Update dashboard
        self.state_manager.update_dashboard(self.metrics)

        print("[Orchestrator] Shutdown complete\n")

    def on_event(self, event: Dict):
        """
        Callback for watchers to submit events.

        Args:
            event: Event dictionary with type, source, timestamp, payload
        """
        with self.event_lock:
            # Check for duplicates in recent window
            if not self._is_duplicate(event):
                self.event_queue.put(event)
                print(f"[Orchestrator] Event queued: {event['type']} from {event['source']}")

    def _is_duplicate(self, event: Dict) -> bool:
        """Check if event is a duplicate within dedup window."""
        # Simple deduplication - can be enhanced
        return False

    def _process_events(self):
        """Main event processing loop."""
        while self.running:
            try:
                # Get event from queue (with timeout)
                try:
                    event = self.event_queue.get(timeout=1)
                except queue.Empty:
                    continue

                # Process event
                self._handle_event(event)

                # Mark as done
                self.event_queue.task_done()

            except Exception as e:
                print(f"[Orchestrator] Error processing event: {e}")

    def _handle_event(self, event: Dict):
        """
        Handle a single event through the full lifecycle.

        Lifecycle:
        1. Load context
        2. Run reasoning engine
        3. Route to appropriate queue
        4. Update dashboard
        """
        print(f"\n[Orchestrator] Processing event: {event['type']}")

        try:
            # Phase 1: Load context
            print("[Orchestrator] Loading context...")
            context = self.context_loader.load_context_for_event(event)

            # Phase 2: Reasoning
            print("[Orchestrator] Running reasoning engine...")
            reasoning = self.reasoning_engine.analyze_event(context)

            # Phase 3: Route task
            print(f"[Orchestrator] Routing task (confidence: {reasoning['confidence']}%)...")
            task_file = self.task_router.route_task(event, reasoning)

            # Update metrics
            self.metrics['tasks_processed'] += 1
            if reasoning['requires_approval']:
                self.metrics['required_approval'] += 1
                print(f"[Orchestrator] Task requires approval: {task_file}")
            else:
                self.metrics['auto_approved'] += 1
                print(f"[Orchestrator] Task auto-approved: {task_file}")

            # Add to recent activity
            activity = f"Processed {event['type']} - {reasoning['decision']['action']}"
            self.metrics['recent_activity'].append(activity)
            if len(self.metrics['recent_activity']) > 20:
                self.metrics['recent_activity'] = self.metrics['recent_activity'][-20:]

            # Phase 4: Update dashboard
            self.state_manager.update_dashboard(self.metrics)

            print(f"[Orchestrator] Event processed successfully\n")

        except Exception as e:
            print(f"[Orchestrator] Error handling event: {e}")
            self.metrics['alerts'].append(f"Event processing error: {str(e)[:50]}")

    def _execute_tasks(self):
        """Execute tasks from Needs_Action queue."""
        while self.running:
            try:
                # Get tasks from Needs_Action
                tasks = self.context_loader.get_needs_action_items()

                for task_file in tasks:
                    print(f"\n[Orchestrator] Executing task: {task_file.name}")

                    # Execute
                    result = self.executor.execute_task(task_file)

                    # Log completion
                    self.state_manager.log_task_completion(task_file, result)

                    # Update metrics
                    self.metrics['recent_activity'].append(
                        f"Executed {task_file.stem}"
                    )

                    print(f"[Orchestrator] Task completed: {result['status']}")

                # Update dashboard
                if tasks:
                    self.state_manager.update_dashboard(self.metrics)

                # Sleep before next check
                time.sleep(5)

            except Exception as e:
                print(f"[Orchestrator] Error in execution loop: {e}")
                time.sleep(5)

    def get_status(self) -> Dict:
        """Get current system status."""
        return {
            'running': self.running,
            'watchers': {
                name: watcher.is_running()
                for name, watcher in self.watchers.items()
            },
            'metrics': self.metrics,
            'queue_size': self.event_queue.qsize()
        }
