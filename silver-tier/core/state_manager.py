"""
State Manager Module
Updates Dashboard.md and manages task lifecycle.
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import shutil


class StateManager:
    """Manages system state and Dashboard updates."""

    def __init__(self, config: Dict):
        self.config = config
        self.memory_path = Path(config['memory']['vault_path'])
        self.dashboard_file = self.memory_path / config['memory']['dashboard']
        self.needs_action_path = self.memory_path / config['memory']['needs_action']
        self.needs_approval_path = self.memory_path / config['memory']['needs_approval']
        self.done_path = self.memory_path / config['memory']['done']

    def update_dashboard(self, metrics: Dict = None):
        """Update Dashboard.md with current state."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Count tasks in each queue
        active_tasks = len(list(self.needs_action_path.glob("*.md"))) if self.needs_action_path.exists() else 0
        pending_approval = len(list(self.needs_approval_path.glob("*.md"))) if self.needs_approval_path.exists() else 0

        # Get metrics
        if metrics is None:
            metrics = self._calculate_metrics()

        # Build dashboard content
        content = f"""# Digital FTE Dashboard

**Last Updated:** {timestamp}
**Status:** 🟢 Operational

---

## Current State

### Active Tasks: {active_tasks}
### Completed Today: {metrics.get('completed_today', 0)}
### Pending Approval: {pending_approval}
### System Health: {metrics.get('health', 'Healthy')}

---

## Recent Activity

"""

        # Add recent activity
        recent = metrics.get('recent_activity', [])
        if recent:
            for activity in recent[-10:]:  # Last 10 items
                content += f"- {activity}\n"
        else:
            content += "*No recent activity*\n"

        content += f"""
---

## Metrics (Last 24h)

- **Tasks Processed:** {metrics.get('tasks_processed', 0)}
- **Auto-Approved:** {metrics.get('auto_approved', 0)}
- **Required Approval:** {metrics.get('required_approval', 0)}
- **MCP Calls Made:** {metrics.get('mcp_calls', 0)}
- **Average Response Time:** {metrics.get('avg_response_time', 'N/A')}

---

## Active Watchers

- [{'X' if metrics.get('file_watcher_active') else ' '}] File Watcher
- [{'X' if metrics.get('time_watcher_active') else ' '}] Time Watcher
- [ ] Email Watcher
- [ ] Webhook Watcher

---

## Alerts

"""

        alerts = metrics.get('alerts', [])
        if alerts:
            for alert in alerts:
                content += f"- ⚠️ {alert}\n"
        else:
            content += "*No alerts*\n"

        content += """
---

## Next Scheduled Tasks

"""

        scheduled = metrics.get('next_scheduled', [])
        if scheduled:
            for task in scheduled:
                content += f"- {task}\n"
        else:
            content += "*No scheduled tasks*\n"

        # Write dashboard
        self.dashboard_file.write_text(content, encoding='utf-8')

    def _calculate_metrics(self) -> Dict:
        """Calculate current metrics."""
        # This is a simple implementation
        # In production, would track metrics in a separate file or database
        return {
            'completed_today': 0,
            'tasks_processed': 0,
            'auto_approved': 0,
            'required_approval': 0,
            'mcp_calls': 0,
            'avg_response_time': 'N/A',
            'health': 'Healthy',
            'recent_activity': [],
            'alerts': [],
            'next_scheduled': [],
            'file_watcher_active': False,
            'time_watcher_active': False
        }

    def move_to_done(self, task_file: Path) -> Path:
        """Move completed task to Done/ archive."""
        if not task_file.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")

        # Create monthly archive folder
        now = datetime.now()
        archive_folder = self.done_path / now.strftime("%Y-%m")
        archive_folder.mkdir(parents=True, exist_ok=True)

        # Move file
        destination = archive_folder / task_file.name
        shutil.move(str(task_file), str(destination))

        return destination

    def add_activity(self, activity: str):
        """Add activity to recent activity log."""
        timestamp = datetime.now().strftime("%H:%M")
        activity_line = f"[{timestamp}] {activity}"

        # This is a simple implementation
        # In production, would maintain a separate activity log
        print(f"[Activity] {activity_line}")

    def log_task_completion(self, task_file: Path, result: Dict):
        """Log task completion and update metrics."""
        # Update task file with completion info
        if task_file.exists():
            content = task_file.read_text(encoding='utf-8')

            # Add execution log
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execution_log = f"""
---

## Execution Log

**Completed:** {timestamp}
**Status:** {result.get('status', 'success')}
**Duration:** {result.get('duration', 'N/A')}

### Results
{result.get('message', 'Task completed successfully')}

### Outputs
"""
            for key, value in result.get('outputs', {}).items():
                execution_log += f"- **{key}:** {value}\n"

            # Append to file
            task_file.write_text(content + execution_log, encoding='utf-8')

        # Move to Done/
        self.move_to_done(task_file)

        # Add activity
        self.add_activity(f"Completed task: {task_file.stem}")
