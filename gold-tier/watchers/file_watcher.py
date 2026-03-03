"""
File Watcher Module
Monitors file system for changes in specified directories.
"""

import time
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Callable
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class FileWatcherHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def __init__(self, callback: Callable, patterns: List[str]):
        self.callback = callback
        self.patterns = patterns
        self.processed_files: Set[str] = set()

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if file matches patterns
        if not any(file_path.match(pattern) for pattern in self.patterns):
            return

        # Avoid duplicate processing
        file_hash = self._get_file_hash(file_path)
        if file_hash in self.processed_files:
            return

        self.processed_files.add(file_hash)

        # Create event object
        event_obj = {
            'type': 'file_change',
            'source': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'payload': {
                'action': 'created',
                'path': str(file_path),
                'filename': file_path.name
            }
        }

        # Call callback
        self.callback(event_obj)

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash of file path and modification time."""
        try:
            stat = file_path.stat()
            hash_input = f"{file_path}:{stat.st_mtime}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except Exception:
            return str(file_path)


class FileWatcher:
    """Watches file system for changes."""

    def __init__(self, config: Dict, event_callback: Callable):
        self.config = config
        self.event_callback = event_callback
        self.observer = None
        self.running = False

    def start(self):
        """Start watching file system."""
        if not self.config.get('enabled', False):
            print("[FileWatcher] Disabled in config")
            return

        watch_paths = self.config.get('watch_paths', [])
        patterns = self.config.get('file_patterns', ['*.md'])

        if not watch_paths:
            print("[FileWatcher] No watch paths configured")
            return

        # Create observer
        self.observer = Observer()
        handler = FileWatcherHandler(self.event_callback, patterns)

        # Schedule watches
        for watch_path in watch_paths:
            path = Path(watch_path)
            if path.exists():
                self.observer.schedule(handler, str(path), recursive=False)
                print(f"[FileWatcher] Watching: {path}")
            else:
                print(f"[FileWatcher] Path does not exist: {path}")

        # Start observer
        self.observer.start()
        self.running = True
        print("[FileWatcher] Started")

    def stop(self):
        """Stop watching file system."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("[FileWatcher] Stopped")

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self.running
