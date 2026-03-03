"""
Context Loader Module
Loads relevant context from memory vault for reasoning engine.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ContextLoader:
    """Loads context from markdown memory vault."""

    def __init__(self, config: Dict):
        self.config = config
        self.memory_path = Path(config['memory']['vault_path'])
        self.dashboard_file = self.memory_path / config['memory']['dashboard']
        self.handbook_file = self.memory_path / config['memory']['handbook']
        self.plan_file = self.memory_path / config['memory']['plan']
        self.skills_path = self.memory_path / config['memory']['skills']

    def load_dashboard(self) -> str:
        """Load current dashboard state."""
        if self.dashboard_file.exists():
            return self.dashboard_file.read_text(encoding='utf-8')
        return "# Dashboard\n\nNo dashboard found."

    def load_handbook(self) -> str:
        """Load company handbook policies."""
        if self.handbook_file.exists():
            return self.handbook_file.read_text(encoding='utf-8')
        return "# Handbook\n\nNo handbook found."

    def load_plan(self) -> str:
        """Load current reasoning plan."""
        if self.plan_file.exists():
            return self.plan_file.read_text(encoding='utf-8')
        return "# Plan\n\nNo active plan."

    def load_skill(self, skill_name: str) -> Optional[str]:
        """Load a specific skill definition."""
        skill_file = self.skills_path / f"{skill_name}.skill.md"
        if skill_file.exists():
            return skill_file.read_text(encoding='utf-8')
        return None

    def list_skills(self) -> List[str]:
        """List all available skills."""
        if not self.skills_path.exists():
            return []

        skills = []
        for file in self.skills_path.glob("*.skill.md"):
            skill_name = file.stem.replace('.skill', '')
            skills.append(skill_name)
        return skills

    def load_context_for_event(self, event: Dict) -> Dict[str, str]:
        """
        Load all relevant context for an event.

        Args:
            event: Event dictionary with type, source, payload

        Returns:
            Dictionary with context sections
        """
        context = {
            'dashboard': self.load_dashboard(),
            'handbook': self.load_handbook(),
            'plan': self.load_plan(),
            'event': event,
            'timestamp': datetime.now().isoformat()
        }

        # Try to match event to a skill
        event_type = event.get('type', '')
        matched_skill = self._match_skill(event_type, event.get('payload', {}))

        if matched_skill:
            skill_content = self.load_skill(matched_skill)
            if skill_content:
                context['matched_skill'] = matched_skill
                context['skill_definition'] = skill_content

        return context

    def _match_skill(self, event_type: str, payload: Dict) -> Optional[str]:
        """
        Match an event to a skill based on type and payload.

        Simple matching logic - can be enhanced with more sophisticated rules.
        """
        # Map event types to skills
        skill_mapping = {
            'email': 'email_responder',
            'scheduled_report': 'report_generator',
            'data_request': 'data_analyzer'
        }

        return skill_mapping.get(event_type)

    def get_inbox_items(self) -> List[Path]:
        """Get all items in Inbox folder."""
        inbox_path = self.memory_path / self.config['memory']['inbox']
        if not inbox_path.exists():
            return []

        return list(inbox_path.glob("*.md"))

    def get_needs_action_items(self) -> List[Path]:
        """Get all items in Needs_Action folder."""
        needs_action_path = self.memory_path / self.config['memory']['needs_action']
        if not needs_action_path.exists():
            return []

        return list(needs_action_path.glob("*.md"))

    def get_needs_approval_items(self) -> List[Path]:
        """Get all items in Needs_Approval folder."""
        needs_approval_path = self.memory_path / self.config['memory']['needs_approval']
        if not needs_approval_path.exists():
            return []

        return list(needs_approval_path.glob("*.md"))
