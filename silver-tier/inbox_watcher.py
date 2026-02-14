#!/usr/bin/env python3
"""
Digital FTE - Inbox Watcher
Monitors AI_Employee_Vault/Inbox/ for new markdown files and triggers automated triage.

Requirements:
    pip install watchdog pyyaml

Usage:
    python inbox_watcher.py
"""

import os
import sys
import time
import logging
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


# Configuration
VAULT_ROOT = Path("AI_Employee_Vault")
INBOX_PATH = VAULT_ROOT / "Inbox"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"
DONE_PATH = VAULT_ROOT / "Done"
DASHBOARD_PATH = VAULT_ROOT / "Dashboard.md"
LOG_PATH = VAULT_ROOT / "watcher.log"

# File stabilization delay (seconds)
FILE_STABLE_DELAY = 2.0

# Processed files tracking (to avoid duplicate processing)
processed_files = set()


class TriageLogger:
    """Centralized logging configuration."""

    @staticmethod
    def setup_logging() -> logging.Logger:
        """Configure logging with file and console handlers."""
        logger = logging.getLogger("DigitalFTE")
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(LOG_PATH)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


class FileManager:
    """Handles file operations with error handling."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file contents with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Read file: {file_path.name}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read {file_path.name}: {e}")
            return None

    def write_file(self, file_path: Path, content: str) -> bool:
        """Write file contents with error handling."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Wrote file: {file_path.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write {file_path.name}: {e}")
            return False

    def move_file(self, source: Path, destination: Path) -> bool:
        """Move file with atomic operation and error handling."""
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Handle filename conflicts
            if destination.exists():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                stem = destination.stem
                suffix = destination.suffix
                destination = destination.parent / f"{stem}_{timestamp}{suffix}"
                self.logger.warning(f"Destination exists, using: {destination.name}")

            # Move file
            source.rename(destination)
            self.logger.info(f"Moved {source.name} -> {destination.parent.name}/")
            return True
        except Exception as e:
            self.logger.error(f"Failed to move {source.name}: {e}")
            return False

    def add_metadata(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Add YAML frontmatter metadata to file."""
        try:
            content = self.read_file(file_path)
            if content is None:
                return False

            # Check if file already has frontmatter
            if content.startswith('---'):
                # Extract existing metadata
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    existing_meta = yaml.safe_load(parts[1])
                    if existing_meta:
                        metadata.update(existing_meta)
                    content = parts[2].lstrip()

            # Create new frontmatter
            frontmatter = "---\n"
            frontmatter += yaml.dump(metadata, default_flow_style=False, sort_keys=False)
            frontmatter += "---\n\n"

            # Write updated content
            new_content = frontmatter + content
            return self.write_file(file_path, new_content)
        except Exception as e:
            self.logger.error(f"Failed to add metadata to {file_path.name}: {e}")
            return False


class ClaudeCodeClient:
    """Handles interaction with Claude Code CLI."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def triage_file(self, file_content: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Call Claude Code CLI to triage a file.
        Returns structured triage result or None on error.
        """
        # Check if Claude CLI is available
        try:
            subprocess.run(['claude', '--version'], capture_output=True, timeout=2)
        except:
            self.logger.warning(f"Claude CLI not available - using default triage for {filename}")
            # Return default triage result
            return {
                'status': 'needs_action',
                'priority': 'P2',
                'complexity': 'moderate',
                'estimated_effort': '1hr',
                'completeness_score': 75,
                'issues': [],
                'reason': 'Default triage (Claude CLI not available)'
            }

        prompt = self._build_triage_prompt(file_content, filename)

        try:
            self.logger.info(f"Calling Claude Code CLI for triage: {filename}")

            # Call Claude Code CLI
            result = subprocess.run(
                ['claude', 'code', '--message', prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.logger.error(f"Claude CLI error: {result.stderr}")
                return None

            # Parse response
            response = result.stdout
            triage_result = self._parse_triage_response(response)

            self.logger.info(f"Triage complete: {filename} -> {triage_result.get('status', 'unknown')}")
            return triage_result

        except subprocess.TimeoutExpired:
            self.logger.error(f"Claude CLI timeout for {filename}")
            return None
        except Exception as e:
            self.logger.error(f"Claude CLI error for {filename}: {e}")
            return None

    def _build_triage_prompt(self, file_content: str, filename: str) -> str:
        """Build structured prompt for triage."""
        return f"""You are the Digital FTE triage system. Analyze this task file and provide a structured triage assessment.

FILE: {filename}

CONTENT:
{file_content}

INSTRUCTIONS:
Follow the triage_file.md skill logic:
1. Validate file structure (title, priority, description, acceptance criteria)
2. Assess priority level (P0-P3)
3. Evaluate completeness (0-100 score)
4. Calculate complexity (simple/moderate/complex)
5. Estimate effort (15min/1hr/4hr/1day/3day)
6. Check for blockers

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "status": "needs_action|needs_clarification|blocked",
  "priority": "P0|P1|P2|P3",
  "complexity": "simple|moderate|complex",
  "estimated_effort": "15min|1hr|4hr|1day|3day",
  "completeness_score": 0-100,
  "issues": ["list of issues if any"],
  "reason": "brief explanation of routing decision"
}}"""

    def _parse_triage_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's triage response into structured data."""
        try:
            # Try to extract JSON from response
            # Claude might wrap it in markdown code blocks
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON object directly
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end].strip()

            result = json.loads(json_str)

            # Validate required fields
            required_fields = ['status', 'priority', 'complexity', 'estimated_effort']
            for field in required_fields:
                if field not in result:
                    self.logger.warning(f"Missing field in triage response: {field}")
                    result[field] = 'unknown'

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from Claude response: {e}")
            self.logger.debug(f"Response was: {response}")
            # Return default triage result
            return {
                'status': 'needs_clarification',
                'priority': 'P2',
                'complexity': 'moderate',
                'estimated_effort': '1hr',
                'completeness_score': 50,
                'issues': ['Failed to parse triage response'],
                'reason': 'Automatic triage failed, manual review required'
            }


class DashboardUpdater:
    """Handles Dashboard.md updates."""

    def __init__(self, logger: logging.Logger, file_manager: FileManager):
        self.logger = logger
        self.file_manager = file_manager

    def log_activity(self, action: str, filename: str, details: str = "") -> bool:
        """Add entry to Dashboard activity log."""
        try:
            dashboard_content = self.file_manager.read_file(DASHBOARD_PATH)
            if dashboard_content is None:
                self.logger.warning("Could not read Dashboard.md")
                return False

            # Create activity entry
            timestamp = datetime.now().strftime("%H:%M")
            entry = f"**{timestamp}** - {action}: {filename}"
            if details:
                entry += f" ({details})"
            entry += "\n"

            # Find activity log section and append
            if "## Activity Log" in dashboard_content:
                # Find the date section
                today = datetime.now().strftime("%Y-%m-%d")
                date_header = f"### {today}"

                if date_header in dashboard_content:
                    # Append to existing date section
                    insert_pos = dashboard_content.find(date_header)
                    # Find end of date section (next ### or ---)
                    next_section = dashboard_content.find("\n---", insert_pos)
                    if next_section == -1:
                        next_section = dashboard_content.find("\n##", insert_pos + len(date_header))

                    if next_section != -1:
                        dashboard_content = (
                            dashboard_content[:next_section] +
                            entry +
                            dashboard_content[next_section:]
                        )
                else:
                    # Create new date section
                    log_section_pos = dashboard_content.find("## Activity Log")
                    next_section = dashboard_content.find("\n---", log_section_pos)
                    new_section = f"\n\n{date_header}\n{entry}"
                    dashboard_content = (
                        dashboard_content[:next_section] +
                        new_section +
                        dashboard_content[next_section:]
                    )

                # Write updated dashboard
                return self.file_manager.write_file(DASHBOARD_PATH, dashboard_content)
            else:
                self.logger.warning("Activity Log section not found in Dashboard.md")
                return False

        except Exception as e:
            self.logger.error(f"Failed to update Dashboard: {e}")
            return False


class TriageProcessor:
    """Orchestrates the triage process."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.file_manager = FileManager(logger)
        self.claude_client = ClaudeCodeClient(logger)
        self.dashboard = DashboardUpdater(logger, self.file_manager)

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file through the triage workflow.
        Returns True if successful, False otherwise.
        """
        filename = file_path.name

        try:
            self.logger.info(f"Processing: {filename}")

            # Step 1: Read file content
            content = self.file_manager.read_file(file_path)
            if content is None:
                return False

            # Step 2: Call Claude for triage
            triage_result = self.claude_client.triage_file(content, filename)
            if triage_result is None:
                self.logger.error(f"Triage failed for {filename}")
                return False

            # Step 3: Add metadata
            metadata = self._build_metadata(triage_result)
            if not self.file_manager.add_metadata(file_path, metadata):
                self.logger.error(f"Failed to add metadata to {filename}")
                return False

            # Step 4: Route file based on triage result
            success = self._route_file(file_path, triage_result)

            # Step 5: Update Dashboard
            if success:
                status = triage_result.get('status', 'unknown')
                priority = triage_result.get('priority', 'P2')
                complexity = triage_result.get('complexity', 'moderate')
                effort = triage_result.get('estimated_effort', '1hr')
                details = f"{priority}, {complexity}, {effort}"
                self.dashboard.log_activity("Triaged task", filename, details)

            return success

        except Exception as e:
            self.logger.error(f"Error processing {filename}: {e}")
            return False

    def _build_metadata(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata dictionary from triage result."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        metadata = {
            'triaged_at': now,
            'triaged_by': 'Digital FTE Watcher',
            'status': triage_result.get('status', 'needs_action'),
            'complexity': triage_result.get('complexity', 'moderate'),
            'estimated_effort': triage_result.get('estimated_effort', '1hr'),
        }

        # Add optional fields
        if 'priority' in triage_result:
            metadata['priority'] = triage_result['priority']

        if 'completeness_score' in triage_result:
            metadata['completeness_score'] = triage_result['completeness_score']

        if triage_result.get('status') in ['needs_action', 'completed']:
            # Calculate SLA deadline based on priority
            priority = triage_result.get('priority', 'P2')
            sla_hours = {'P0': 0, 'P1': 4, 'P2': 24, 'P3': 72}.get(priority, 24)
            from datetime import timedelta
            deadline = datetime.now() + timedelta(hours=sla_hours)
            metadata['sla_deadline'] = deadline.strftime("%Y-%m-%d %H:%M")

        return metadata

    def _route_file(self, file_path: Path, triage_result: Dict[str, Any]) -> bool:
        """Route file to appropriate folder based on triage result."""
        status = triage_result.get('status', 'needs_action')
        filename = file_path.name

        if status == 'needs_action':
            # Move to Needs_Action folder
            destination = NEEDS_ACTION_PATH / filename
            return self.file_manager.move_file(file_path, destination)

        elif status == 'needs_clarification':
            # Rename with [CLARIFICATION] prefix and keep in Inbox
            new_filename = f"[CLARIFICATION]-{filename}"
            destination = INBOX_PATH / new_filename
            return self.file_manager.move_file(file_path, destination)

        elif status == 'blocked':
            # Rename with [BLOCKED] prefix and keep in Inbox
            new_filename = f"[BLOCKED]-{filename}"
            destination = INBOX_PATH / new_filename
            return self.file_manager.move_file(file_path, destination)

        elif status == 'completed':
            # Move directly to Done (rare case)
            destination = DONE_PATH / filename
            return self.file_manager.move_file(file_path, destination)

        else:
            self.logger.warning(f"Unknown status '{status}' for {filename}, moving to Needs_Action")
            destination = NEEDS_ACTION_PATH / filename
            return self.file_manager.move_file(file_path, destination)


class InboxWatcherHandler(FileSystemEventHandler):
    """Handles file system events for the Inbox folder."""

    def __init__(self, processor: TriageProcessor, logger: logging.Logger):
        self.processor = processor
        self.logger = logger
        self.pending_files = {}  # Track files waiting for stabilization

    def on_created(self, event: FileCreatedEvent):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix.lower() != '.md':
            self.logger.info(f"Ignored non-markdown file: {file_path.name}")
            return

        # Skip files with prefixes (already processed)
        if file_path.name.startswith('[CLARIFICATION]') or file_path.name.startswith('[BLOCKED]'):
            return

        # Skip if already processed
        if str(file_path) in processed_files:
            return

        self.logger.info(f"New file detected: {file_path.name}")

        # Schedule processing after stabilization delay
        self.pending_files[str(file_path)] = time.time()

    def process_pending_files(self):
        """Process files that have stabilized."""
        current_time = time.time()
        files_to_process = []

        for file_path_str, detection_time in list(self.pending_files.items()):
            if current_time - detection_time >= FILE_STABLE_DELAY:
                files_to_process.append(file_path_str)
                del self.pending_files[file_path_str]

        for file_path_str in files_to_process:
            file_path = Path(file_path_str)

            # Verify file still exists
            if not file_path.exists():
                self.logger.warning(f"File disappeared: {file_path.name}")
                continue

            # Process the file
            success = self.processor.process_file(file_path)

            if success:
                processed_files.add(file_path_str)
            else:
                self.logger.error(f"Failed to process: {file_path.name}")


def verify_environment(logger: logging.Logger) -> bool:
    """Verify that the environment is set up correctly."""
    # Check if vault directories exist
    required_dirs = [VAULT_ROOT, INBOX_PATH, NEEDS_ACTION_PATH, DONE_PATH]

    for directory in required_dirs:
        if not directory.exists():
            logger.error(f"Required directory not found: {directory}")
            return False

    # Check if Dashboard exists
    if not DASHBOARD_PATH.exists():
        logger.error(f"Dashboard not found: {DASHBOARD_PATH}")
        return False

    # Check if Claude Code CLI is available (optional)
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.warning("Claude Code CLI not found - triage will be skipped")
            logger.warning("Install Claude CLI from: https://claude.ai/download")
        else:
            logger.info(f"Claude Code CLI detected: {result.stdout.strip()}")
    except Exception as e:
        logger.warning(f"Claude Code CLI not available: {e}")
        logger.warning("Watcher will run but skip automatic triage")
        logger.warning("Install Claude CLI from: https://claude.ai/download")

    return True


def main():
    """Main entry point for the inbox watcher."""
    # Setup logging
    logger = TriageLogger.setup_logging()
    logger.info("=" * 60)
    logger.info("Digital FTE Inbox Watcher Starting")
    logger.info("=" * 60)

    # Verify environment
    if not verify_environment(logger):
        logger.error("Environment verification failed. Exiting.")
        sys.exit(1)

    logger.info(f"Monitoring: {INBOX_PATH.absolute()}")

    # Create processor and handler
    processor = TriageProcessor(logger)
    event_handler = InboxWatcherHandler(processor, logger)

    # Setup observer
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_PATH), recursive=False)
    observer.start()

    logger.info("Watcher active. Press Ctrl+C to stop.")

    try:
        while True:
            # Process pending files every second
            event_handler.process_pending_files()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested...")
        observer.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        observer.stop()

    observer.join()
    logger.info("Digital FTE Inbox Watcher stopped.")


if __name__ == "__main__":
    main()
