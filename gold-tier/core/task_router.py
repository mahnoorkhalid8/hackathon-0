"""
Task Router Module
Routes tasks to appropriate queues based on approval rules.
"""

from pathlib import Path
from typing import Dict
from datetime import datetime
import yaml


class TaskRouter:
    """Routes tasks to Needs_Action or Needs_Approval queues."""

    def __init__(self, config: Dict):
        self.config = config
        self.memory_path = Path(config['memory']['vault_path'])
        self.needs_action_path = self.memory_path / config['memory']['needs_action']
        self.needs_approval_path = self.memory_path / config['memory']['needs_approval']

        # Load approval rules
        rules_file = Path(config['approval']['rules_file'])
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                self.approval_rules = yaml.safe_load(f)
        else:
            self.approval_rules = {'auto_approve': [], 'require_approval': []}

    def route_task(self, event: Dict, reasoning: Dict) -> Path:
        """
        Route task to appropriate queue.

        Args:
            event: Original event
            reasoning: Reasoning engine output

        Returns:
            Path to created task file
        """
        # Check if approval required
        requires_approval = self._check_approval_required(event, reasoning)

        # Generate task file
        task_content = self._generate_task_content(event, reasoning)

        # Determine destination
        if requires_approval:
            task_file = self._create_task_file(
                self.needs_approval_path,
                task_content,
                event
            )
        else:
            task_file = self._create_task_file(
                self.needs_action_path,
                task_content,
                event
            )

        return task_file

    def _check_approval_required(self, event: Dict, reasoning: Dict) -> bool:
        """
        Check if task requires approval based on rules and reasoning.
        """
        # If reasoning engine says approval required
        if reasoning.get('requires_approval', False):
            return True

        # If confidence is low
        if reasoning.get('confidence', 0) < 80:
            return True

        # Check explicit approval rules
        event_type = event.get('type', '')

        # Check auto-approve rules
        for rule in self.approval_rules.get('auto_approve', []):
            if self._matches_rule(event, rule):
                return False

        # Check require-approval rules
        for rule in self.approval_rules.get('require_approval', []):
            if self._matches_rule(event, rule):
                return True

        # Default to requiring approval (safety first)
        return True

    def _matches_rule(self, event: Dict, rule: Dict) -> bool:
        """Check if event matches a rule."""
        # Simple rule matching - can be enhanced

        # Check skill match
        if 'skill' in rule:
            matched_skill = event.get('matched_skill', '')
            if matched_skill != rule['skill']:
                return False

        # Check action type
        if 'action_type' in rule:
            if event.get('action_type') != rule['action_type']:
                return False

        # Check MCP call requirement
        if rule.get('any_mcp_call'):
            if event.get('requires_mcp', False):
                return True

        return True

    def _generate_task_content(self, event: Dict, reasoning: Dict) -> str:
        """Generate task file content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = f"""# Task: {event.get('type', 'Unknown')}

**Created:** {timestamp}
**Status:** Pending
**Confidence:** {reasoning.get('confidence', 0)}%

---

## Event Details

**Type:** {event.get('type', 'unknown')}
**Source:** {event.get('source', 'unknown')}
**Timestamp:** {event.get('timestamp', 'unknown')}

### Payload
"""

        payload = event.get('payload', {})
        for key, value in payload.items():
            content += f"- **{key}:** {value}\n"

        content += f"""
---

## Reasoning Summary

**Situation:** {reasoning.get('situation', 'N/A')[:200]}...

**Decision:** {reasoning.get('decision', {}).get('action', 'unknown')}
**Reason:** {reasoning.get('decision', {}).get('reason', 'N/A')}

### Analysis Steps
"""

        for i, step in enumerate(reasoning.get('analysis', []), 1):
            content += f"{i}. {step}\n"

        content += """
---

## Approval Decision

*Awaiting human review*

Status: [ ] APPROVED | [ ] REJECTED | [ ] MODIFIED

**Notes:**


**Modified Action (if applicable):**


---

## Execution Log

*Will be populated upon execution*
"""

        return content

    def _create_task_file(self, destination: Path, content: str, event: Dict) -> Path:
        """Create task file in destination folder."""
        # Ensure destination exists
        destination.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        event_type = event.get('type', 'unknown').replace(' ', '_')
        filename = f"task-{timestamp}-{event_type}.md"

        task_file = destination / filename
        task_file.write_text(content, encoding='utf-8')

        return task_file
