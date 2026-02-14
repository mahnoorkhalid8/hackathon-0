"""
Silver Tier Digital FTE - Agent Orchestration Script

This script orchestrates the execution of various agent tasks including
watchers, scheduled reports, and one-off operations.

Usage:
    python run_agent.py watchers              # Run all watchers once
    python run_agent.py file-watcher          # Run file watcher only
    python run_agent.py gmail-watcher         # Run Gmail watcher only
    python run_agent.py ceo-report            # Generate CEO report
    python run_agent.py task --file <path>    # Process specific task file

Author: Digital FTE System
Date: 2026-02-13
"""

import sys
import os
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file at startup
load_env()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Digital FTE components
try:
    from file_watcher_service import FileWatcherService
    from gmail_watcher_service import GmailWatcherService
    from iterative_reasoning_engine import IterativeReasoningEngine
    from core.orchestrator import Orchestrator
    from core.context_loader import ContextLoader
except ImportError as e:
    print(f"Error importing components: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging for orchestration script."""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = log_dir / f"run_agent_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("run_agent")
    return logger


# ============================================================================
# Agent Orchestrator
# ============================================================================

class AgentOrchestrator:
    """Orchestrates execution of Digital FTE agent tasks."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time = datetime.now()

    def run_watchers(self) -> Dict[str, Any]:
        """Run all watchers (file and Gmail)."""

        self.logger.info("=" * 70)
        self.logger.info("Running all watchers")
        self.logger.info("=" * 70)

        results = {
            "file_watcher": None,
            "gmail_watcher": None,
            "success": True,
            "errors": []
        }

        # Run file watcher
        try:
            self.logger.info("Starting file watcher...")
            results["file_watcher"] = self.run_file_watcher()
        except Exception as e:
            self.logger.error(f"File watcher failed: {e}")
            results["success"] = False
            results["errors"].append(f"File watcher: {str(e)}")

        # Run Gmail watcher
        try:
            self.logger.info("Starting Gmail watcher...")
            results["gmail_watcher"] = self.run_gmail_watcher()
        except Exception as e:
            self.logger.error(f"Gmail watcher failed: {e}")
            results["success"] = False
            results["errors"].append(f"Gmail watcher: {str(e)}")

        self.logger.info("=" * 70)
        self.logger.info(f"Watchers completed: {results['success']}")
        self.logger.info("=" * 70)

        return results

    def run_file_watcher(self) -> Dict[str, Any]:
        """Run file watcher once."""

        self.logger.info("Initializing file watcher service...")

        # Load configuration
        config_path = Path("config/file_watcher_config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        # Initialize service
        service = FileWatcherService(str(config_path))

        # Check for new files
        inbox_path = Path("memory/Inbox")
        if not inbox_path.exists():
            self.logger.warning(f"Inbox directory not found: {inbox_path}")
            return {"files_processed": 0, "success": True}

        # Get list of files
        files = list(inbox_path.glob("*.md"))
        self.logger.info(f"Found {len(files)} file(s) in Inbox")

        processed = 0
        for file_path in files:
            try:
                self.logger.info(f"Processing: {file_path.name}")
                # Trigger agent loop for this file
                self._trigger_agent_loop(str(file_path))
                processed += 1
            except Exception as e:
                self.logger.error(f"Failed to process {file_path.name}: {e}")

        result = {
            "files_found": len(files),
            "files_processed": processed,
            "success": processed == len(files)
        }

        self.logger.info(f"File watcher result: {result}")
        return result

    def run_gmail_watcher(self) -> Dict[str, Any]:
        """Run Gmail watcher once."""

        self.logger.info("Initializing Gmail watcher service...")

        # Load configuration
        config_path = Path("config/gmail_watcher_config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        # Initialize service
        service = GmailWatcherService(str(config_path))

        # Check for new emails
        self.logger.info("Checking for unread emails...")
        result = service.check_and_process_emails()

        self.logger.info(f"Gmail watcher result: {result}")
        return result

    def run_ceo_report(self) -> Dict[str, Any]:
        """Generate and send CEO report."""

        self.logger.info("=" * 70)
        self.logger.info("Generating CEO Report")
        self.logger.info("=" * 70)

        try:
            # Import CEO briefing generator
            from generate_ceo_briefing import TaskAnalyzer, BriefingGenerator

            # Analyze tasks
            self.logger.info("Analyzing tasks...")
            analyzer = TaskAnalyzer("memory")
            analysis = analyzer.analyze_all()

            self.logger.info(f"  Completed: {analysis['metrics']['completed_count']}")
            self.logger.info(f"  Pending: {analysis['metrics']['pending_count']}")
            self.logger.info(f"  Bottlenecks: {len(analysis['bottlenecks'])}")

            # Generate briefing
            self.logger.info("Generating briefing...")
            generator = BriefingGenerator()
            briefing = generator.generate(analysis)

            # Save to Dashboard.md
            dashboard_path = Path("memory/Dashboard.md")
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(briefing)

            self.logger.info(f"Briefing saved to: {dashboard_path}")

            # Also save to reports directory
            reports_dir = Path("memory/reports")
            reports_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = reports_dir / f"ceo_briefing_{timestamp}.md"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(briefing)

            self.logger.info(f"Briefing archived to: {report_path}")

            # Send report via email (if configured)
            email_result = self._send_briefing_email(briefing)

            result = {
                "success": True,
                "dashboard_path": str(dashboard_path),
                "report_path": str(report_path),
                "email_sent": email_result.get("success", False),
                "metrics": analysis["metrics"],
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info("CEO briefing generated successfully")
            return result

        except Exception as e:
            self.logger.error(f"CEO briefing generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_task_file(self, file_path: str) -> Dict[str, Any]:
        """Process a specific task file."""

        self.logger.info(f"Processing task file: {file_path}")

        try:
            # Read task file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Trigger agent loop
            result = self._trigger_agent_loop(file_path)

            return {
                "success": True,
                "file": file_path,
                "result": result
            }

        except Exception as e:
            self.logger.error(f"Task file processing failed: {e}")
            return {
                "success": False,
                "file": file_path,
                "error": str(e)
            }

    def _trigger_agent_loop(self, file_path: str) -> Dict[str, Any]:
        """Trigger agent loop for a file."""

        self.logger.info(f"Triggering agent loop for: {file_path}")

        # Initialize reasoning engine
        engine = IterativeReasoningEngine()

        # Create task from file
        task = {
            "source_file": file_path,
            "timestamp": datetime.now().isoformat(),
            "objective": f"Process file: {Path(file_path).name}"
        }

        # Execute with reasoning engine
        result = engine.execute_task(task)

        return result

    def _generate_ceo_report(self, context: Dict[str, Any]) -> str:
        """Generate CEO report content."""

        # Get current week number
        week_num = datetime.now().isocalendar()[1]

        # Build report
        report = f"""# CEO Weekly Report - Week {week_num}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report provides a summary of Digital FTE operations for Week {week_num}.

## System Status

- **Orchestrator Status:** {context.get('orchestrator_status', 'Running')}
- **Active Tasks:** {context.get('active_tasks', 0)}
- **Completed Tasks:** {context.get('completed_tasks', 0)}
- **Pending Approvals:** {context.get('pending_approvals', 0)}

## Key Metrics

### Email Operations
- **Emails Sent:** {context.get('emails_sent', 0)}
- **Emails Received:** {context.get('emails_received', 0)}
- **Email Success Rate:** {context.get('email_success_rate', '100%')}

### Task Processing
- **Tasks Processed:** {context.get('tasks_processed', 0)}
- **Average Processing Time:** {context.get('avg_processing_time', 'N/A')}
- **Success Rate:** {context.get('task_success_rate', '100%')}

### Approval Workflow
- **Approvals Requested:** {context.get('approvals_requested', 0)}
- **Approvals Granted:** {context.get('approvals_granted', 0)}
- **Approvals Rejected:** {context.get('approvals_rejected', 0)}
- **Approvals Expired:** {context.get('approvals_expired', 0)}

## Notable Events

{self._format_notable_events(context.get('notable_events', []))}

## Recommendations

{self._format_recommendations(context.get('recommendations', []))}

## Next Week Priorities

{self._format_priorities(context.get('priorities', []))}

---

*This report was automatically generated by the Digital FTE system.*
"""

        return report

    def _format_notable_events(self, events: list) -> str:
        """Format notable events section."""
        if not events:
            return "- No notable events this week"

        return "\n".join(f"- {event}" for event in events)

    def _format_recommendations(self, recommendations: list) -> str:
        """Format recommendations section."""
        if not recommendations:
            return "- No recommendations at this time"

        return "\n".join(f"- {rec}" for rec in recommendations)

    def _format_priorities(self, priorities: list) -> str:
        """Format priorities section."""
        if not priorities:
            return "- Continue normal operations"

        return "\n".join(f"{i+1}. {priority}" for i, priority in enumerate(priorities))

    def _save_report(self, report: str) -> Path:
        """Save report to file."""

        # Create reports directory
        reports_dir = Path("memory/reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ceo_report_{timestamp}.md"
        report_path = reports_dir / filename

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        self.logger.info(f"Report saved: {report_path}")
        return report_path

    def _send_briefing_email(self, briefing: str) -> Dict[str, Any]:
        """Send briefing via Gmail API."""

        try:
            from gmail_api_service import GmailAPIService

            # Get CEO email from config
            ceo_email = os.getenv("CEO_EMAIL", "khalidmahnoor889@gmail.com")

            # Get credentials path from config
            credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
            token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")

            week_num = datetime.now().isocalendar()[1]
            subject = f"Monday Morning CEO Briefing - Week {week_num}"

            # Initialize Gmail API service
            self.logger.info("Initializing Gmail API service...")
            gmail = GmailAPIService(credentials_path=credentials_path, token_path=token_path)

            # Send email
            self.logger.info(f"Sending briefing email to {ceo_email}...")
            result = gmail.send_email(
                to=ceo_email,
                subject=subject,
                body=briefing
            )

            if result.get("success"):
                self.logger.info(f"Briefing email sent successfully to {ceo_email}")
                self.logger.info(f"Message ID: {result.get('message_id')}")
            else:
                self.logger.error(f"Failed to send email: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to send briefing email: {e}")
            return {"success": False, "error": str(e)}

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""

        duration = (datetime.now() - self.start_time).total_seconds()

        return {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": duration,
            "success": True
        }


# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Silver Tier Digital FTE - Agent Orchestration Script"
    )

    parser.add_argument(
        "command",
        choices=["watchers", "file-watcher", "gmail-watcher", "ceo-report", "task"],
        help="Command to execute"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Task file path (required for 'task' command)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_level)

    logger.info("=" * 70)
    logger.info("Silver Tier Digital FTE - Agent Orchestration")
    logger.info("=" * 70)
    logger.info(f"Command: {args.command}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    # Create orchestrator
    orchestrator = AgentOrchestrator(logger)

    # Execute command
    try:
        if args.command == "watchers":
            result = orchestrator.run_watchers()

        elif args.command == "file-watcher":
            result = orchestrator.run_file_watcher()

        elif args.command == "gmail-watcher":
            result = orchestrator.run_gmail_watcher()

        elif args.command == "ceo-report":
            result = orchestrator.run_ceo_report()

        elif args.command == "task":
            if not args.file:
                logger.error("--file argument required for 'task' command")
                sys.exit(1)
            result = orchestrator.run_task_file(args.file)

        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)

        # Log result
        logger.info("=" * 70)
        logger.info("Execution Result:")
        logger.info(json.dumps(result, indent=2))
        logger.info("=" * 70)

        # Get summary
        summary = orchestrator.get_execution_summary()
        logger.info(f"Duration: {summary['duration_seconds']:.2f} seconds")

        # Exit with appropriate code
        exit_code = 0 if result.get("success", True) else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
