"""
Monday Morning CEO Briefing Generator

Analyzes completed and pending tasks to generate a comprehensive
executive briefing with metrics, bottlenecks, and recommendations.

Usage:
    python generate_ceo_briefing.py
    python generate_ceo_briefing.py --output vault/Dashboard.md

Author: Digital FTE System
Date: 2026-02-13
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import re


# ============================================================================
# Task Analyzer
# ============================================================================

class TaskAnalyzer:
    """Analyzes tasks from vault directories."""

    def __init__(self, vault_path: str = "memory"):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.needs_approval_path = self.vault_path / "Needs_Approval"
        self.inbox_path = self.vault_path / "Inbox"

    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all tasks and return comprehensive metrics."""

        # Get current week info
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)

        analysis = {
            "timestamp": now.isoformat(),
            "week_number": now.isocalendar()[1],
            "start_date": week_start.strftime("%Y-%m-%d"),
            "end_date": week_end.strftime("%Y-%m-%d"),
            "completed_tasks": self.analyze_completed_tasks(),
            "pending_tasks": self.analyze_pending_tasks(),
            "approval_tasks": self.analyze_approval_tasks(),
            "inbox_tasks": self.analyze_inbox_tasks(),
            "metrics": {},
            "bottlenecks": [],
            "priorities": [],
            "insights": []
        }

        # Calculate metrics
        analysis["metrics"] = self.calculate_metrics(analysis)

        # Identify bottlenecks
        analysis["bottlenecks"] = self.identify_bottlenecks(analysis)

        # Generate priorities
        analysis["priorities"] = self.generate_priorities(analysis)

        # Generate insights
        analysis["insights"] = self.generate_insights(analysis)

        return analysis

    def analyze_completed_tasks(self) -> List[Dict[str, Any]]:
        """Analyze completed tasks from Done directory."""

        tasks = []

        if not self.done_path.exists():
            return tasks

        for file_path in self.done_path.glob("*.md"):
            try:
                task = self.parse_task_file(file_path)
                task["status"] = "completed"
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        # Sort by completion date (most recent first)
        tasks.sort(key=lambda x: x.get("completed_at", ""), reverse=True)

        return tasks

    def analyze_pending_tasks(self) -> List[Dict[str, Any]]:
        """Analyze pending tasks from Needs_Action directory."""

        tasks = []

        if not self.needs_action_path.exists():
            return tasks

        for file_path in self.needs_action_path.glob("*.md"):
            try:
                task = self.parse_task_file(file_path)
                task["status"] = "pending"
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        # Sort by priority and age
        tasks.sort(key=lambda x: (
            self.priority_score(x.get("priority", "medium")),
            x.get("created_at", "")
        ), reverse=True)

        return tasks

    def analyze_approval_tasks(self) -> List[Dict[str, Any]]:
        """Analyze tasks awaiting approval."""

        tasks = []

        if not self.needs_approval_path.exists():
            return tasks

        for file_path in self.needs_approval_path.glob("*.md"):
            try:
                task = self.parse_task_file(file_path)
                task["status"] = "awaiting_approval"
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        return tasks

    def analyze_inbox_tasks(self) -> List[Dict[str, Any]]:
        """Analyze new tasks in Inbox."""

        tasks = []

        if not self.inbox_path.exists():
            return tasks

        for file_path in self.inbox_path.glob("*.md"):
            try:
                task = self.parse_task_file(file_path)
                task["status"] = "new"
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        return tasks

    def parse_task_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a task file and extract metadata."""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        task = {
            "file": file_path.name,
            "path": str(file_path),
            "title": file_path.stem,
            "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        }

        # Parse frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    task.update(frontmatter)
                except:
                    pass

        # Extract title from content if not in frontmatter
        if "title" not in task or not task["title"]:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    task["title"] = line[2:].strip()
                    break

        # Calculate age in days
        created = datetime.fromisoformat(task["created_at"])
        age_days = (datetime.now() - created).days
        task["age_days"] = age_days

        return task

    def priority_score(self, priority: str) -> int:
        """Convert priority to numeric score."""
        scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return scores.get(priority.lower(), 2)

    def calculate_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics."""

        completed = analysis["completed_tasks"]
        pending = analysis["pending_tasks"]
        approval = analysis["approval_tasks"]

        # Get tasks from this week
        week_start = datetime.fromisoformat(analysis["start_date"])
        week_completed = [
            t for t in completed
            if datetime.fromisoformat(t.get("completed_at", t["modified_at"])) >= week_start
        ]

        total_tasks = len(completed) + len(pending) + len(approval)
        completion_rate = (len(completed) / total_tasks * 100) if total_tasks > 0 else 0

        # Calculate average completion time
        completion_times = []
        for task in week_completed:
            if "created_at" in task and "completed_at" in task:
                created = datetime.fromisoformat(task["created_at"])
                completed_dt = datetime.fromisoformat(task["completed_at"])
                hours = (completed_dt - created).total_seconds() / 3600
                completion_times.append(hours)

        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        # Task distribution by type
        task_types = defaultdict(int)
        for task in week_completed:
            task_type = task.get("type", "other")
            task_types[task_type] += 1

        metrics = {
            "completed_count": len(completed),
            "pending_count": len(pending),
            "approval_count": len(approval),
            "inbox_count": len(analysis["inbox_tasks"]),
            "week_completed_count": len(week_completed),
            "completion_rate": round(completion_rate, 1),
            "avg_completion_time": round(avg_completion_time, 1),
            "tasks_per_day": round(len(week_completed) / 7, 1),
            "task_types": dict(task_types),
            "aging_tasks": len([t for t in pending if t["age_days"] > 7]),
            "blocked_tasks": len([t for t in pending if t.get("blocked", False)])
        }

        return metrics

    def identify_bottlenecks(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify bottlenecks and blockers."""

        bottlenecks = []
        pending = analysis["pending_tasks"]
        metrics = analysis["metrics"]

        # Aging tasks
        aging_tasks = [t for t in pending if t["age_days"] > 7]
        if aging_tasks:
            bottlenecks.append({
                "type": "aging_tasks",
                "severity": "high" if len(aging_tasks) > 5 else "medium",
                "title": f"{len(aging_tasks)} tasks aging (>7 days)",
                "description": f"Tasks have been pending for over a week",
                "tasks": aging_tasks[:5],  # Top 5
                "recommendation": "Review and prioritize or delegate these tasks"
            })

        # Blocked tasks
        blocked_tasks = [t for t in pending if t.get("blocked", False)]
        if blocked_tasks:
            bottlenecks.append({
                "type": "blocked_tasks",
                "severity": "critical",
                "title": f"{len(blocked_tasks)} tasks blocked",
                "description": "Tasks cannot proceed due to dependencies",
                "tasks": blocked_tasks,
                "recommendation": "Resolve blockers or escalate"
            })

        # High approval backlog
        if metrics["approval_count"] > 5:
            bottlenecks.append({
                "type": "approval_backlog",
                "severity": "medium",
                "title": f"{metrics['approval_count']} tasks awaiting approval",
                "description": "Approval queue is building up",
                "recommendation": "Review and approve/reject pending requests"
            })

        # Low completion rate
        if metrics["completion_rate"] < 50:
            bottlenecks.append({
                "type": "low_completion",
                "severity": "high",
                "title": f"Low completion rate ({metrics['completion_rate']}%)",
                "description": "More tasks pending than completed",
                "recommendation": "Focus on completing existing tasks before starting new ones"
            })

        return bottlenecks

    def generate_priorities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommended priorities."""

        priorities = []
        pending = analysis["pending_tasks"]
        bottlenecks = analysis["bottlenecks"]

        # Priority 1: Unblock blocked tasks
        blocked = [t for t in pending if t.get("blocked", False)]
        if blocked:
            priorities.append({
                "rank": 1,
                "title": f"Unblock {len(blocked)} blocked task(s)",
                "reason": "Blocked tasks prevent progress on dependent work",
                "impact": "High - enables downstream tasks",
                "effort": "Medium",
                "tasks": blocked[:3]
            })

        # Priority 2: Complete aging tasks
        aging = [t for t in pending if t["age_days"] > 7]
        if aging:
            priorities.append({
                "rank": 2,
                "title": f"Complete {len(aging)} aging task(s)",
                "reason": "Tasks have been pending for over a week",
                "impact": "Medium - reduces backlog",
                "effort": "Varies",
                "tasks": aging[:3]
            })

        # Priority 3: High priority pending tasks
        high_priority = [t for t in pending if t.get("priority", "medium") in ["high", "critical"]]
        if high_priority:
            priorities.append({
                "rank": 3,
                "title": f"Address {len(high_priority)} high-priority task(s)",
                "reason": "Marked as high priority by requester",
                "impact": "High - critical business needs",
                "effort": "Varies",
                "tasks": high_priority[:3]
            })

        # Quick wins
        quick_wins = [
            t for t in pending
            if t.get("effort", "medium") == "low" and t["age_days"] < 3
        ]
        if quick_wins:
            priorities.append({
                "rank": 4,
                "title": f"Quick wins: {len(quick_wins)} low-effort task(s)",
                "reason": "Easy wins to boost momentum",
                "impact": "Low-Medium",
                "effort": "Low",
                "tasks": quick_wins[:5]
            })

        return priorities[:3]  # Top 3 priorities

    def generate_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights and recommendations."""

        insights = []
        metrics = analysis["metrics"]
        completed = analysis["completed_tasks"]

        # Trend analysis
        if metrics["week_completed_count"] > 0:
            insights.append({
                "type": "trend",
                "title": "Productivity Trend",
                "description": f"Completed {metrics['week_completed_count']} tasks this week",
                "sentiment": "positive" if metrics["week_completed_count"] >= 5 else "neutral"
            })

        # Task type distribution
        if metrics["task_types"]:
            top_type = max(metrics["task_types"].items(), key=lambda x: x[1])
            insights.append({
                "type": "distribution",
                "title": "Task Distribution",
                "description": f"Most common task type: {top_type[0]} ({top_type[1]} tasks)",
                "sentiment": "neutral"
            })

        # Efficiency insight
        if metrics["avg_completion_time"] > 0:
            if metrics["avg_completion_time"] < 24:
                insights.append({
                    "type": "efficiency",
                    "title": "Fast Turnaround",
                    "description": f"Average completion time: {metrics['avg_completion_time']:.1f} hours",
                    "sentiment": "positive"
                })
            elif metrics["avg_completion_time"] > 72:
                insights.append({
                    "type": "efficiency",
                    "title": "Slow Turnaround",
                    "description": f"Average completion time: {metrics['avg_completion_time']:.1f} hours",
                    "sentiment": "negative",
                    "recommendation": "Consider breaking down large tasks"
                })

        return insights


# ============================================================================
# Briefing Generator
# ============================================================================

class BriefingGenerator:
    """Generates CEO briefing from analysis."""

    def __init__(self, template_path: str = "templates/monday-briefing-template.md"):
        self.template_path = Path(template_path)

    def generate(self, analysis: Dict[str, Any]) -> str:
        """Generate briefing from analysis."""

        # Load template
        if self.template_path.exists():
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            template = self._get_default_template()

        # Fill template
        briefing = self._fill_template(template, analysis)

        return briefing

    def _fill_template(self, template: str, analysis: Dict[str, Any]) -> str:
        """Fill template with analysis data."""

        metrics = analysis["metrics"]
        completed = analysis["completed_tasks"]
        pending = analysis["pending_tasks"]
        approval = analysis["approval_tasks"]
        bottlenecks = analysis["bottlenecks"]
        priorities = analysis["priorities"]
        insights = analysis["insights"]

        # Basic replacements
        replacements = {
            "{{TIMESTAMP}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "{{WEEK_NUMBER}}": str(analysis["week_number"]),
            "{{START_DATE}}": analysis["start_date"],
            "{{END_DATE}}": analysis["end_date"],
            "{{COMPLETED_COUNT}}": str(metrics["completed_count"]),
            "{{PENDING_COUNT}}": str(metrics["pending_count"]),
            "{{BLOCKED_COUNT}}": str(metrics["blocked_tasks"]),
            "{{COMPLETION_RATE}}": str(metrics["completion_rate"]),
            "{{IN_PROGRESS_COUNT}}": str(len([t for t in pending if t.get("status") == "in_progress"])),
            "{{APPROVAL_COUNT}}": str(metrics["approval_count"]),
            "{{AVG_COMPLETION_TIME}}": f"{metrics['avg_completion_time']:.1f} hours",
            "{{TASKS_PER_DAY}}": str(metrics["tasks_per_day"]),
        }

        # Executive summary
        summary = self._generate_executive_summary(analysis)
        replacements["{{EXECUTIVE_SUMMARY}}"] = summary

        # Completed tasks list
        completed_list = self._format_task_list(completed[:10])  # Top 10
        replacements["{{COMPLETED_TASKS_LIST}}"] = completed_list

        # Pending tasks list
        pending_list = self._format_task_list(pending[:10])
        replacements["{{PENDING_TASKS_LIST}}"] = pending_list

        # Approval tasks list
        approval_list = self._format_task_list(approval)
        replacements["{{APPROVAL_TASKS_LIST}}"] = approval_list

        # Bottlenecks section
        bottlenecks_section = self._format_bottlenecks(bottlenecks)
        replacements["{{BOTTLENECKS_SECTION}}"] = bottlenecks_section

        # Priorities
        for i, priority in enumerate(priorities[:3], 1):
            replacements[f"{{{{PRIORITY_{i}_TITLE}}}}"] = priority["title"]
            replacements[f"{{{{PRIORITY_{i}_REASON}}}}"] = priority["reason"]
            replacements[f"{{{{PRIORITY_{i}_IMPACT}}}}"] = priority["impact"]
            replacements[f"{{{{PRIORITY_{i}_EFFORT}}}}"] = priority["effort"]

        # Fill in missing priorities
        for i in range(len(priorities) + 1, 4):
            replacements[f"{{{{PRIORITY_{i}_TITLE}}}}"] = "No additional priorities"
            replacements[f"{{{{PRIORITY_{i}_REASON}}}}"] = "N/A"
            replacements[f"{{{{PRIORITY_{i}_IMPACT}}}}"] = "N/A"
            replacements[f"{{{{PRIORITY_{i}_EFFORT}}}}"] = "N/A"

        # Apply replacements
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)

        # Remove remaining placeholders
        template = re.sub(r'\{\{[A-Z_0-9]+\}\}', 'N/A', template)

        return template

    def _generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate executive summary."""

        metrics = analysis["metrics"]
        bottlenecks = analysis["bottlenecks"]

        summary_parts = []

        # Overall status
        if metrics["completion_rate"] >= 70:
            summary_parts.append("Strong progress this week with high completion rate.")
        elif metrics["completion_rate"] >= 50:
            summary_parts.append("Steady progress this week with moderate completion rate.")
        else:
            summary_parts.append("Limited progress this week. Focus needed on task completion.")

        # Bottlenecks
        if bottlenecks:
            critical = [b for b in bottlenecks if b["severity"] == "critical"]
            if critical:
                summary_parts.append(f"{len(critical)} critical bottleneck(s) require immediate attention.")

        # Positive note
        if metrics["week_completed_count"] > 0:
            summary_parts.append(f"Team completed {metrics['week_completed_count']} tasks this week.")

        return " ".join(summary_parts)

    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for display."""

        if not tasks:
            return "*No tasks*"

        lines = []
        for task in tasks:
            title = task.get("title", task.get("file", "Untitled"))
            age = task.get("age_days", 0)
            priority = task.get("priority", "medium")

            line = f"- **{title}**"
            if age > 7:
                line += f" ⚠️ ({age} days old)"
            if priority in ["high", "critical"]:
                line += f" 🔴 {priority.upper()}"

            lines.append(line)

        return "\n".join(lines)

    def _format_bottlenecks(self, bottlenecks: List[Dict[str, Any]]) -> str:
        """Format bottlenecks section."""

        if not bottlenecks:
            return "*No significant bottlenecks identified.*"

        lines = []
        for bottleneck in bottlenecks:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(bottleneck["severity"], "⚪")

            lines.append(f"### {severity_emoji} {bottleneck['title']}")
            lines.append(f"{bottleneck['description']}")
            lines.append(f"**Recommendation:** {bottleneck['recommendation']}")
            lines.append("")

        return "\n".join(lines)

    def _get_default_template(self) -> str:
        """Return default template if file not found."""
        return """# Monday Morning CEO Briefing

**Generated:** {{TIMESTAMP}}
**Week:** {{WEEK_NUMBER}}

## Executive Summary
{{EXECUTIVE_SUMMARY}}

## Progress
- Completed: {{COMPLETED_COUNT}}
- Pending: {{PENDING_COUNT}}
- Completion Rate: {{COMPLETION_RATE}}%

## Completed Tasks
{{COMPLETED_TASKS_LIST}}

## Pending Tasks
{{PENDING_TASKS_LIST}}

## Bottlenecks
{{BOTTLENECKS_SECTION}}

## Priorities
1. {{PRIORITY_1_TITLE}}
2. {{PRIORITY_2_TITLE}}
3. {{PRIORITY_3_TITLE}}
"""


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Generate Monday Morning CEO Briefing"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="memory/Dashboard.md",
        help="Output file path"
    )
    parser.add_argument(
        "--vault",
        type=str,
        default="memory",
        help="Vault directory path"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("  Monday Morning CEO Briefing Generator")
    print("=" * 70)
    print()

    # Analyze tasks
    print("[1/3] Analyzing tasks...")
    analyzer = TaskAnalyzer(args.vault)
    analysis = analyzer.analyze_all()

    print(f"  Completed: {analysis['metrics']['completed_count']}")
    print(f"  Pending: {analysis['metrics']['pending_count']}")
    print(f"  Awaiting Approval: {analysis['metrics']['approval_count']}")
    print(f"  Bottlenecks: {len(analysis['bottlenecks'])}")

    # Generate briefing
    print("\n[2/3] Generating briefing...")
    generator = BriefingGenerator()
    briefing = generator.generate(analysis)

    print(f"  Generated {len(briefing)} characters")

    # Save briefing
    print(f"\n[3/3] Saving to {args.output}...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)

    print(f"  Saved: {output_path}")

    print("\n" + "=" * 70)
    print("  Briefing generated successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
