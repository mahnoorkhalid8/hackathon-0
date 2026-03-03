"""
Executor Module
Executes approved tasks from Needs_Action queue.
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import time


class Executor:
    """Executes approved tasks."""

    def __init__(self, config: Dict, mcp_client=None):
        self.config = config
        self.mcp_client = mcp_client
        self.memory_path = Path(config['memory']['vault_path'])
        self.skills_path = self.memory_path / config['memory']['skills']

    def execute_task(self, task_file: Path) -> Dict:
        """
        Execute a task from Needs_Action queue.

        Args:
            task_file: Path to task file

        Returns:
            Dictionary with execution results
        """
        start_time = time.time()

        try:
            # Read task file
            task_content = task_file.read_text(encoding='utf-8')

            # Parse task details
            task_info = self._parse_task_file(task_content)

            # Load skill definition
            skill_name = task_info.get('skill')
            if not skill_name:
                return {
                    'status': 'error',
                    'message': 'No skill specified in task',
                    'duration': f"{time.time() - start_time:.2f}s"
                }

            skill_def = self._load_skill(skill_name)
            if not skill_def:
                return {
                    'status': 'error',
                    'message': f'Skill not found: {skill_name}',
                    'duration': f"{time.time() - start_time:.2f}s"
                }

            # Execute skill steps
            result = self._execute_skill(skill_def, task_info)

            # Add duration
            result['duration'] = f"{time.time() - start_time:.2f}s"

            return result

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Execution failed: {str(e)}',
                'duration': f"{time.time() - start_time:.2f}s"
            }

    def _parse_task_file(self, content: str) -> Dict:
        """Parse task file to extract key information."""
        info = {}

        # Extract event type
        if "**Type:**" in content:
            start = content.find("**Type:**") + len("**Type:**")
            end = content.find("\n", start)
            info['event_type'] = content[start:end].strip()

        # Extract decision
        if "**Decision:**" in content:
            start = content.find("**Decision:**") + len("**Decision:**")
            end = content.find("\n", start)
            decision = content[start:end].strip()
            info['decision'] = decision

        # Try to infer skill from event type
        event_type = info.get('event_type', '')
        if 'email' in event_type.lower():
            info['skill'] = 'email_responder'
        elif 'report' in event_type.lower():
            info['skill'] = 'report_generator'

        return info

    def _load_skill(self, skill_name: str) -> Optional[Dict]:
        """Load skill definition."""
        skill_file = self.skills_path / f"{skill_name}.skill.md"
        if not skill_file.exists():
            return None

        content = skill_file.read_text(encoding='utf-8')

        # Parse skill definition
        skill = {
            'name': skill_name,
            'content': content
        }

        # Extract execution steps
        if "## Execution Steps" in content:
            start = content.find("## Execution Steps")
            end = content.find("\n##", start + 1)
            if end == -1:
                end = len(content)
            steps_section = content[start:end]

            # Parse numbered steps
            steps = []
            for line in steps_section.split('\n'):
                if line.strip() and line[0].isdigit():
                    steps.append(line.strip())
            skill['steps'] = steps

        return skill

    def _execute_skill(self, skill_def: Dict, task_info: Dict) -> Dict:
        """
        Execute skill steps.

        This is a simplified implementation. In production, each skill
        would have its own execution logic.
        """
        skill_name = skill_def['name']
        steps = skill_def.get('steps', [])

        print(f"[Executor] Executing skill: {skill_name}")
        print(f"[Executor] Steps to execute: {len(steps)}")

        # Simulate execution
        outputs = {}

        if skill_name == 'email_responder':
            outputs = self._execute_email_responder(task_info)
        elif skill_name == 'report_generator':
            outputs = self._execute_report_generator(task_info)
        else:
            outputs = {
                'message': f'Skill {skill_name} executed (simulated)',
                'steps_completed': len(steps)
            }

        return {
            'status': 'success',
            'message': f'Skill {skill_name} completed successfully',
            'outputs': outputs
        }

    def _execute_email_responder(self, task_info: Dict) -> Dict:
        """Execute email responder skill."""
        # Simulated email response
        return {
            'action': 'email_draft_created',
            'draft_location': 'memory/Needs_Approval/email_draft.md',
            'note': 'Email draft created and moved to approval queue'
        }

    def _execute_report_generator(self, task_info: Dict) -> Dict:
        """Execute report generator skill."""
        # Simulated report generation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"report_{timestamp}.md"

        return {
            'action': 'report_generated',
            'report_file': f'memory/Done/{report_file}',
            'data_points': 42,
            'note': 'Report generated successfully'
        }

    def requires_mcp(self, task_file: Path) -> bool:
        """Check if task requires MCP call."""
        content = task_file.read_text(encoding='utf-8')

        # Check for MCP indicators
        mcp_keywords = ['external', 'api', 'mcp', 'web', 'fetch']

        return any(keyword in content.lower() for keyword in mcp_keywords)
