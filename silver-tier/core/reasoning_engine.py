"""
Reasoning Engine Module
Updates Plan.md with iterative reasoning for each task.
"""

from pathlib import Path
from typing import Dict, Tuple, List
from datetime import datetime
import re


class ReasoningEngine:
    """Handles reasoning loop and Plan.md updates."""

    def __init__(self, config: Dict):
        self.config = config
        self.memory_path = Path(config['memory']['vault_path'])
        self.plan_file = self.memory_path / config['memory']['plan']

    def analyze_event(self, context: Dict) -> Dict:
        """
        Analyze an event and generate reasoning.

        Args:
            context: Full context including event, dashboard, handbook, skills

        Returns:
            Dictionary with analysis results
        """
        event = context['event']

        # Extract key information
        situation = self._describe_situation(event)
        relevant_policies = self._extract_policies(context.get('handbook', ''))
        skill_info = self._analyze_skill(context.get('skill_definition', ''))

        # Perform step-by-step analysis
        analysis_steps = self._generate_analysis(event, skill_info, relevant_policies)

        # Make decision
        decision, confidence = self._make_decision(analysis_steps, skill_info)

        # Update Plan.md
        self._update_plan(situation, relevant_policies, analysis_steps, decision, confidence)

        return {
            'situation': situation,
            'analysis': analysis_steps,
            'decision': decision,
            'confidence': confidence,
            'requires_approval': confidence < 80 or decision.get('action') == 'require_approval'
        }

    def _describe_situation(self, event: Dict) -> str:
        """Generate human-readable situation description."""
        event_type = event.get('type', 'unknown')
        source = event.get('source', 'unknown')
        payload = event.get('payload', {})

        description = f"Event Type: {event_type}\n"
        description += f"Source: {source}\n"
        description += f"Timestamp: {event.get('timestamp', 'unknown')}\n\n"

        if payload:
            description += "Payload Details:\n"
            for key, value in payload.items():
                description += f"- {key}: {value}\n"

        return description

    def _extract_policies(self, handbook: str) -> str:
        """Extract relevant policies from handbook."""
        # Simple extraction - look for approval requirements
        policies = []

        if "Require Approval:" in handbook:
            # Extract the section
            start = handbook.find("Require Approval:")
            end = handbook.find("\n\n", start)
            if end > start:
                policies.append(handbook[start:end])

        if "Auto-Approve:" in handbook:
            start = handbook.find("Auto-Approve:")
            end = handbook.find("\n\n", start)
            if end > start:
                policies.append(handbook[start:end])

        return "\n\n".join(policies) if policies else "No specific policies found."

    def _analyze_skill(self, skill_definition: str) -> Dict:
        """Extract key information from skill definition."""
        if not skill_definition:
            return {'found': False}

        info = {'found': True}

        # Extract approval requirements
        if "Approval Required: Yes" in skill_definition:
            info['requires_approval'] = True
        elif "Approval Required: No" in skill_definition:
            info['requires_approval'] = False
        else:
            info['requires_approval'] = None  # Conditional

        # Extract auto-approve conditions
        if "## Auto-Approve Conditions" in skill_definition:
            start = skill_definition.find("## Auto-Approve Conditions")
            end = skill_definition.find("\n##", start + 1)
            if end == -1:
                end = len(skill_definition)
            info['auto_approve_conditions'] = skill_definition[start:end]

        return info

    def _generate_analysis(self, event: Dict, skill_info: Dict, policies: str) -> List[str]:
        """Generate step-by-step analysis."""
        steps = []

        # Step 1: What is being requested?
        steps.append(f"What is being requested? Event type '{event.get('type')}' from {event.get('source')}")

        # Step 2: What skill applies?
        if skill_info.get('found'):
            steps.append(f"Matched skill found with approval requirement: {skill_info.get('requires_approval')}")
        else:
            steps.append("No matching skill found - will require approval")

        # Step 3: What are the constraints?
        steps.append(f"Policy constraints: {policies[:100]}...")

        # Step 4: What are the risks?
        risks = []
        if event.get('type') == 'file_change' and 'Inbox' in event.get('source', ''):
            risks.append("New file in Inbox - unknown content")
        if not skill_info.get('found'):
            risks.append("No skill match - uncertain execution path")

        steps.append(f"Identified risks: {', '.join(risks) if risks else 'Low risk'}")

        return steps

    def _make_decision(self, analysis_steps: List[str], skill_info: Dict) -> Tuple[Dict, int]:
        """
        Make a decision based on analysis.

        Returns:
            Tuple of (decision dict, confidence level 0-100)
        """
        # Default to requiring approval
        decision = {
            'action': 'require_approval',
            'reason': 'Default safety policy'
        }
        confidence = 50

        # If skill found and has clear approval rules
        if skill_info.get('found'):
            if skill_info.get('requires_approval') is False:
                decision = {
                    'action': 'auto_execute',
                    'reason': 'Skill explicitly allows auto-execution'
                }
                confidence = 85
            elif skill_info.get('requires_approval') is True:
                decision = {
                    'action': 'require_approval',
                    'reason': 'Skill requires human approval'
                }
                confidence = 90

        # Check for high-risk indicators
        risk_keywords = ['delete', 'external', 'mcp', 'api']
        analysis_text = ' '.join(analysis_steps).lower()

        if any(keyword in analysis_text for keyword in risk_keywords):
            decision['action'] = 'require_approval'
            decision['reason'] = 'High-risk operation detected'
            confidence = max(confidence, 70)

        return decision, confidence

    def _update_plan(self, situation: str, policies: str, analysis: List[str],
                     decision: Dict, confidence: int):
        """Update Plan.md with current reasoning."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        plan_content = f"""# Current Reasoning Plan

**Session Started:** {timestamp}
**Status:** Active

---

## Current Situation

{situation}

---

## Context

### Relevant Policies
{policies}

---

## Analysis

"""

        for i, step in enumerate(analysis, 1):
            plan_content += f"{i}. {step}\n"

        plan_content += f"""
---

## Decision

**Action:** {decision['action']}
**Reason:** {decision['reason']}

---

## Confidence Level

{confidence}% - {"High" if confidence >= 80 else "Medium" if confidence >= 60 else "Low"}

---

## Next Steps

"""

        if decision['action'] == 'require_approval':
            plan_content += "1. Create task file in Needs_Approval/\n"
            plan_content += "2. Wait for human review\n"
            plan_content += "3. Execute upon approval\n"
        else:
            plan_content += "1. Create task file in Needs_Action/\n"
            plan_content += "2. Execute immediately\n"
            plan_content += "3. Update Dashboard with results\n"

        # Write to Plan.md
        self.plan_file.write_text(plan_content, encoding='utf-8')
