"""
Human-in-the-Loop Approval System - Implementation

This module provides a complete approval workflow for sensitive actions.
Integrates with existing TaskRouter and Executor components.

Author: Digital FTE System
Date: 2026-02-13
"""

import os
import time
import yaml
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Configuration and Constants
# ============================================================================

class ApprovalStatus(Enum):
    """Approval request status states."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ActionType(Enum):
    """Types of actions that may require approval."""
    EMAIL = "email"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_POST = "twitter_post"
    API_CALL = "api_call"
    FILE_DELETE = "file_delete"
    DATABASE_WRITE = "database_write"
    FINANCIAL = "financial"
    SYSTEM_CONFIG = "system_config"


class ImpactLevel(Enum):
    """Impact level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Reversibility(Enum):
    """Action reversibility classification."""
    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ApprovalRequest:
    """Represents an approval request."""
    approval_id: str
    created_at: datetime
    status: ApprovalStatus
    action_type: ActionType
    priority: str
    expires_at: datetime
    requested_by: str
    action_title: str
    action_description: str
    mcp_server: str
    method: str
    parameters: Dict[str, Any]
    context: str
    reasoning: str
    expected_outcome: str
    impact_level: ImpactLevel
    reversibility: Reversibility
    scope: str
    data_sensitivity: str
    risks: List[Dict[str, str]]
    safeguards: List[str]
    policy_status: str
    preview_data: Optional[Dict[str, Any]] = None
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    approval_comments: Optional[str] = None


@dataclass
class ApprovalDecision:
    """Represents a human decision on an approval request."""
    approval_id: str
    status: ApprovalStatus
    decided_by: str
    decided_at: datetime
    comments: str


# ============================================================================
# Approval Manager
# ============================================================================

class ApprovalManager:
    """
    Manages the complete lifecycle of approval requests.

    Responsibilities:
    - Create approval requests for sensitive actions
    - Monitor approval files for human decisions
    - Handle timeouts and expirations
    - Archive completed approvals
    - Integrate with TaskRouter and Executor
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ApprovalManager.

        Args:
            config: Configuration dictionary with paths and settings
        """
        self.config = config
        self.vault_path = Path(config.get("vault_path", "memory"))
        self.needs_approval_path = self.vault_path / "Needs_Approval"
        self.done_path = self.vault_path / "Done"
        self.template_path = Path(config.get("template_path", "templates"))

        # Approval settings
        self.poll_interval = config.get("poll_interval_seconds", 30)
        self.default_timeout = config.get("default_timeout_seconds", 3600)

        # Ensure directories exist
        self.needs_approval_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("ApprovalManager")
        self.logger.setLevel(logging.INFO)

        # Load approval rules
        self.approval_rules = self._load_approval_rules()

        # Active monitoring threads
        self.active_monitors = {}


    def _load_approval_rules(self) -> Dict[str, Any]:
        """Load approval rules from configuration."""
        rules_path = Path("config/approval_rules.yaml")

        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f)

        # Default rules if file doesn't exist
        return {
            "sensitive_actions": [
                "send_email",
                "post_linkedin",
                "post_twitter",
                "external_api_call",
                "delete_file",
                "database_write",
                "financial_transaction"
            ],
            "auto_approve": [],
            "always_require_approval": [
                "financial_transaction",
                "database_write"
            ],
            "timeout_by_priority": {
                "low": 7200,      # 2 hours
                "medium": 3600,   # 1 hour
                "high": 1800,     # 30 minutes
                "critical": 900   # 15 minutes
            }
        }


    def is_sensitive_action(self, task: Dict[str, Any]) -> bool:
        """
        Determine if a task requires human approval.

        Args:
            task: Task dictionary with action details

        Returns:
            True if approval is required, False otherwise
        """
        action_type = task.get("action_type", "")
        impact_level = task.get("impact_level", "low")
        data_sensitivity = task.get("data_sensitivity", "none")
        reversibility = task.get("reversibility", "reversible")

        # Check if action type is in sensitive list
        if action_type in self.approval_rules["sensitive_actions"]:
            return True

        # Check if always requires approval
        if action_type in self.approval_rules["always_require_approval"]:
            return True

        # Check impact level
        if impact_level in ["high", "critical"]:
            return True

        # Check data sensitivity
        if data_sensitivity in ["high", "pii"]:
            return True

        # Check reversibility
        if reversibility == "irreversible":
            return True

        # Check company policy
        if self._violates_policy(task):
            return True

        return False


    def _violates_policy(self, task: Dict[str, Any]) -> bool:
        """
        Check if task violates company policies.

        Args:
            task: Task dictionary

        Returns:
            True if policy violation detected
        """
        # Email policy checks
        if task.get("action_type") == "send_email":
            content = task.get("content", "")
            recipients = task.get("recipients", [])

            # Check for PII in email
            if self._contains_pii(content):
                return True

            # Check for external recipients
            if self._has_external_recipients(recipients):
                return True

        # Financial policy checks
        if task.get("action_type") == "financial_transaction":
            amount = task.get("amount", 0)
            if amount > 1000:  # Threshold for approval
                return True

        # Social media policy checks
        if task.get("action_type") in ["post_linkedin", "post_twitter"]:
            # All social media posts require approval
            return True

        return False


    def _contains_pii(self, content: str) -> bool:
        """Check if content contains PII."""
        # Simplified PII detection
        pii_patterns = [
            "ssn", "social security",
            "credit card", "card number",
            "password", "secret",
            "bank account"
        ]

        content_lower = content.lower()
        return any(pattern in content_lower for pattern in pii_patterns)


    def _has_external_recipients(self, recipients: List[str]) -> bool:
        """Check if recipients include external addresses."""
        company_domains = self.config.get("company_domains", ["company.com"])

        for recipient in recipients:
            domain = recipient.split("@")[-1] if "@" in recipient else ""
            if domain not in company_domains:
                return True

        return False


    def create_approval_request(
        self,
        task: Dict[str, Any],
        action_details: Dict[str, Any]
    ) -> str:
        """
        Create an approval request file.

        Args:
            task: Task dictionary
            action_details: Detailed action information

        Returns:
            approval_id: Unique identifier for the approval request
        """
        # Generate unique approval ID
        approval_id = self._generate_approval_id()

        # Determine timeout based on priority
        priority = task.get("priority", "medium")
        timeout_seconds = self.approval_rules["timeout_by_priority"].get(
            priority,
            self.default_timeout
        )

        # Create approval request object
        approval_request = ApprovalRequest(
            approval_id=approval_id,
            created_at=datetime.now(),
            status=ApprovalStatus.PENDING,
            action_type=ActionType(task.get("action_type", "api_call")),
            priority=priority,
            expires_at=datetime.now() + timedelta(seconds=timeout_seconds),
            requested_by=task.get("requested_by", "agent"),
            action_title=task.get("title", "Untitled Action"),
            action_description=action_details.get("description", ""),
            mcp_server=action_details.get("mcp_server", ""),
            method=action_details.get("method", ""),
            parameters=action_details.get("parameters", {}),
            context=action_details.get("context", ""),
            reasoning=action_details.get("reasoning", ""),
            expected_outcome=action_details.get("expected_outcome", ""),
            impact_level=ImpactLevel(task.get("impact_level", "medium")),
            reversibility=Reversibility(task.get("reversibility", "reversible")),
            scope=task.get("scope", "internal"),
            data_sensitivity=task.get("data_sensitivity", "none"),
            risks=action_details.get("risks", []),
            safeguards=action_details.get("safeguards", []),
            policy_status=action_details.get("policy_status", "compliant"),
            preview_data=action_details.get("preview_data")
        )

        # Generate approval file content
        approval_content = self._generate_approval_file(approval_request)

        # Write to Needs_Approval directory
        file_path = self.needs_approval_path / f"{approval_id}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        self.logger.info(
            f"Approval request created: {approval_id} "
            f"(type={approval_request.action_type.value}, "
            f"priority={priority}, "
            f"expires_in={timeout_seconds}s)"
        )

        return approval_id


    def _generate_approval_id(self) -> str:
        """Generate unique approval ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Find next available sequence number
        existing_files = list(self.needs_approval_path.glob(f"APR-{timestamp[:8]}-*.md"))
        sequence = len(existing_files) + 1

        return f"APR-{timestamp[:8]}-{sequence:03d}"


    def _generate_approval_file(self, request: ApprovalRequest) -> str:
        """
        Generate approval file content from template.

        Args:
            request: ApprovalRequest object

        Returns:
            Formatted approval file content
        """
        # Load template
        template_path = self.template_path / "approval-request-template.md"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            # Use inline template if file doesn't exist
            template = self._get_default_template()

        # Replace placeholders
        content = template
        replacements = {
            "{{APPROVAL_ID}}": request.approval_id,
            "{{TIMESTAMP_ISO}}": request.created_at.isoformat(),
            "{{STATUS}}": request.status.value,
            "{{ACTION_TYPE}}": request.action_type.value,
            "{{PRIORITY}}": request.priority,
            "{{EXPIRY_TIMESTAMP}}": request.expires_at.isoformat(),
            "{{AGENT_NAME}}": request.requested_by,
            "{{ACTION_TITLE}}": request.action_title,
            "{{ACTION_DESCRIPTION}}": request.action_description,
            "{{MCP_SERVER_NAME}}": request.mcp_server,
            "{{METHOD_NAME}}": request.method,
            "{{PARAMETERS_YAML}}": yaml.dump(request.parameters, indent=2),
            "{{CONTEXT_DESCRIPTION}}": request.context,
            "{{REASONING_BULLETS}}": request.reasoning,
            "{{EXPECTED_OUTCOME}}": request.expected_outcome,
            "{{IMPACT_LEVEL}}": request.impact_level.value,
            "{{REVERSIBILITY}}": request.reversibility.value,
            "{{SCOPE}}": request.scope,
            "{{DATA_SENSITIVITY}}": request.data_sensitivity,
            "{{POLICY_STATUS}}": request.policy_status,
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))

        # Add risks
        if request.risks:
            risks_text = ""
            for i, risk in enumerate(request.risks, 1):
                risks_text += f"\n{i}. **{risk.get('title', 'Risk')}**\n"
                risks_text += f"   - Likelihood: {risk.get('likelihood', 'unknown')}\n"
                risks_text += f"   - Impact: {risk.get('impact', 'unknown')}\n"
                risks_text += f"   - Mitigation: {risk.get('mitigation', 'none')}\n"
            content = content.replace("{{RISKS_LIST}}", risks_text)

        # Add safeguards
        if request.safeguards:
            safeguards_text = "\n".join(f"- {s}" for s in request.safeguards)
            content = content.replace("{{SAFEGUARDS_LIST}}", safeguards_text)

        # Add preview data if available
        if request.preview_data:
            preview_text = self._format_preview(request.action_type, request.preview_data)
            content = content.replace("{{PREVIEW_SECTION}}", preview_text)

        return content


    def _get_default_template(self) -> str:
        """Return default approval template if file doesn't exist."""
        return """---
id: "{{APPROVAL_ID}}"
created_at: "{{TIMESTAMP_ISO}}"
status: "{{STATUS}}"
action_type: "{{ACTION_TYPE}}"
priority: "{{PRIORITY}}"
expires_at: "{{EXPIRY_TIMESTAMP}}"
---

# Approval Request: {{ACTION_TITLE}}

## Action Details
{{ACTION_DESCRIPTION}}

## MCP Execution
Server: {{MCP_SERVER_NAME}}
Method: {{METHOD_NAME}}

## Risk Analysis
Impact: {{IMPACT_LEVEL}}
Reversibility: {{REVERSIBILITY}}

## Human Instructions
To approve: Change status to "APPROVED" and save.
To reject: Change status to "REJECTED" and save.
"""


    def _format_preview(
        self,
        action_type: ActionType,
        preview_data: Dict[str, Any]
    ) -> str:
        """Format preview section based on action type."""

        if action_type == ActionType.EMAIL:
            return f"""
### Email Preview
```
To: {preview_data.get('to', 'N/A')}
Subject: {preview_data.get('subject', 'N/A')}

{preview_data.get('body', 'N/A')}
```
"""

        elif action_type == ActionType.LINKEDIN_POST:
            return f"""
### LinkedIn Post Preview
```
{preview_data.get('content', 'N/A')}
```
"""

        elif action_type == ActionType.API_CALL:
            return f"""
### API Call Preview
```json
{yaml.dump(preview_data, indent=2)}
```
"""

        return ""


    def monitor_approval(
        self,
        approval_id: str,
        timeout_seconds: Optional[int] = None
    ) -> Tuple[ApprovalStatus, Optional[ApprovalDecision]]:
        """
        Monitor an approval request until decision or timeout.

        Args:
            approval_id: Approval request ID
            timeout_seconds: Optional custom timeout

        Returns:
            Tuple of (status, decision)
        """
        if timeout_seconds is None:
            timeout_seconds = self.default_timeout

        start_time = time.time()
        file_path = self.needs_approval_path / f"{approval_id}.md"

        self.logger.info(
            f"Monitoring approval {approval_id} "
            f"(timeout={timeout_seconds}s, poll_interval={self.poll_interval}s)"
        )

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                self.logger.warning(f"Approval {approval_id} expired after {elapsed:.0f}s")
                self._mark_expired(approval_id)
                return ApprovalStatus.EXPIRED, None

            # Check if file still exists
            if not file_path.exists():
                self.logger.error(f"Approval file {approval_id} was deleted")
                return ApprovalStatus.REJECTED, None

            # Read current status
            try:
                decision = self._read_approval_decision(file_path)

                if decision.status == ApprovalStatus.APPROVED:
                    self.logger.info(
                        f"Approval {approval_id} APPROVED by {decision.decided_by}"
                    )
                    return ApprovalStatus.APPROVED, decision

                elif decision.status == ApprovalStatus.REJECTED:
                    self.logger.info(
                        f"Approval {approval_id} REJECTED by {decision.decided_by}: "
                        f"{decision.comments}"
                    )
                    return ApprovalStatus.REJECTED, decision

                # Still pending
                remaining = timeout_seconds - elapsed
                self.logger.debug(
                    f"Approval {approval_id} still pending "
                    f"(remaining={remaining:.0f}s)"
                )

            except Exception as e:
                self.logger.error(f"Error reading approval {approval_id}: {e}")

            # Wait before next check
            time.sleep(self.poll_interval)


    def _read_approval_decision(self, file_path: Path) -> ApprovalDecision:
        """
        Read approval decision from file.

        Args:
            file_path: Path to approval file

        Returns:
            ApprovalDecision object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])

                status_str = frontmatter.get("status", "PENDING")
                status = ApprovalStatus(status_str)

                return ApprovalDecision(
                    approval_id=frontmatter.get("id", ""),
                    status=status,
                    decided_by=frontmatter.get("decided_by", ""),
                    decided_at=datetime.fromisoformat(
                        frontmatter.get("decided_at", datetime.now().isoformat())
                    ),
                    comments=frontmatter.get("approval_comments", "")
                )

        # Default to pending if can't parse
        return ApprovalDecision(
            approval_id="",
            status=ApprovalStatus.PENDING,
            decided_by="",
            decided_at=datetime.now(),
            comments=""
        )


    def _mark_expired(self, approval_id: str) -> None:
        """Mark an approval request as expired."""
        file_path = self.needs_approval_path / f"{approval_id}.md"

        if file_path.exists():
            # Update status in file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update frontmatter status
            content = content.replace(
                'status: "PENDING"',
                'status: "EXPIRED"'
            )
            content = content.replace(
                'status: PENDING',
                'status: EXPIRED'
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Archive to Done
            self._archive_approval(approval_id, "EXPIRED")


    def _archive_approval(
        self,
        approval_id: str,
        final_status: str
    ) -> None:
        """
        Move approval file to Done directory.

        Args:
            approval_id: Approval request ID
            final_status: Final status (APPROVED, REJECTED, EXPIRED, EXECUTED, FAILED)
        """
        source_path = self.needs_approval_path / f"{approval_id}.md"
        dest_path = self.done_path / f"{approval_id}-{final_status}.md"

        if source_path.exists():
            # Move file
            source_path.rename(dest_path)
            self.logger.info(f"Archived approval {approval_id} with status {final_status}")
        else:
            self.logger.warning(f"Cannot archive {approval_id}: file not found")


    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """
        Get list of all pending approval requests.

        Returns:
            List of approval summaries
        """
        pending = []

        for file_path in self.needs_approval_path.glob("APR-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])

                        if frontmatter.get("status") == "PENDING":
                            pending.append({
                                "id": frontmatter.get("id"),
                                "action_type": frontmatter.get("action_type"),
                                "priority": frontmatter.get("priority"),
                                "created_at": frontmatter.get("created_at"),
                                "expires_at": frontmatter.get("expires_at"),
                                "file_path": str(file_path)
                            })

            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")

        return pending


# ============================================================================
# Integration with Task Router
# ============================================================================

def integrate_with_task_router(task_router, approval_manager):
    """
    Integrate ApprovalManager with existing TaskRouter.

    Modifies TaskRouter.route_task() to check for sensitive actions.
    """

    original_route_task = task_router.route_task

    def route_task_with_approval(task: Dict[str, Any]) -> str:
        """Enhanced routing with approval check."""

        # Check if action requires approval
        if approval_manager.is_sensitive_action(task):
            return "needs_approval"

        # Otherwise use original routing logic
        return original_route_task(task)

    # Replace method
    task_router.route_task = route_task_with_approval


# ============================================================================
# Integration with Executor
# ============================================================================

def integrate_with_executor(executor, approval_manager):
    """
    Integrate ApprovalManager with existing Executor.

    Adds approval workflow before execution of sensitive actions.
    """

    original_execute = executor.execute

    def execute_with_approval_check(task: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced execution with approval check."""

        # Check if this task requires approval
        if approval_manager.is_sensitive_action(task):

            # Create approval request
            approval_id = approval_manager.create_approval_request(
                task=task,
                action_details=task.get("action_details", {})
            )

            # Monitor for decision
            status, decision = approval_manager.monitor_approval(approval_id)

            if status == ApprovalStatus.APPROVED:
                # Execute the action
                result = original_execute(task)

                # Archive as executed
                approval_manager._archive_approval(approval_id, "EXECUTED")

                return {
                    "status": "success",
                    "approval_id": approval_id,
                    "result": result
                }

            elif status == ApprovalStatus.REJECTED:
                # Don't execute, return rejection
                approval_manager._archive_approval(approval_id, "REJECTED")

                return {
                    "status": "rejected",
                    "approval_id": approval_id,
                    "reason": decision.comments if decision else "No reason provided"
                }

            else:  # EXPIRED
                # Don't execute, return timeout
                return {
                    "status": "expired",
                    "approval_id": approval_id,
                    "reason": "Approval request timed out"
                }

        else:
            # No approval needed, execute directly
            return original_execute(task)

    # Replace method
    executor.execute = execute_with_approval_check


# ============================================================================
# Main Workflow Example
# ============================================================================

def main():
    """
    Example usage of the approval system.
    """

    # Initialize components
    config = {
        "vault_path": "memory",
        "template_path": "templates",
        "poll_interval_seconds": 30,
        "default_timeout_seconds": 3600,
        "company_domains": ["company.com"]
    }

    approval_manager = ApprovalManager(config)

    # Example: Send email task
    email_task = {
        "action_type": "send_email",
        "title": "Send weekly report to client",
        "priority": "high",
        "impact_level": "medium",
        "reversibility": "irreversible",
        "data_sensitivity": "low",
        "scope": "external",
        "requested_by": "agent",
        "action_details": {
            "description": "Send weekly sales report to client contact",
            "mcp_server": "email_server",
            "method": "send_email",
            "parameters": {
                "to": "client@external.com",
                "subject": "Weekly Sales Report - Week 7",
                "body": "Please find attached the weekly sales report..."
            },
            "context": "Client requested weekly reports every Monday",
            "reasoning": "Scheduled task triggered by time watcher",
            "expected_outcome": "Client receives report and confirms receipt",
            "risks": [
                {
                    "title": "Email delivery failure",
                    "likelihood": "low",
                    "impact": "medium",
                    "mitigation": "Retry mechanism in place"
                },
                {
                    "title": "Incorrect data in report",
                    "likelihood": "low",
                    "impact": "high",
                    "mitigation": "Data validation performed before sending"
                }
            ],
            "safeguards": [
                "Email content reviewed by data validation",
                "Recipient verified against CRM",
                "Attachment scanned for sensitive data"
            ],
            "policy_status": "compliant",
            "preview_data": {
                "to": "client@external.com",
                "subject": "Weekly Sales Report - Week 7",
                "body": "Please find attached the weekly sales report..."
            }
        }
    }

    # Check if approval is needed
    if approval_manager.is_sensitive_action(email_task):
        print("[INFO] Action requires approval")

        # Create approval request
        approval_id = approval_manager.create_approval_request(
            task=email_task,
            action_details=email_task["action_details"]
        )

        print(f"[INFO] Approval request created: {approval_id}")
        print(f"[INFO] File: memory/Needs_Approval/{approval_id}.md")
        print("[INFO] Waiting for human decision...")

        # Monitor for decision (with 1 hour timeout)
        status, decision = approval_manager.monitor_approval(
            approval_id,
            timeout_seconds=3600
        )

        if status == ApprovalStatus.APPROVED:
            print(f"[SUCCESS] Approved by {decision.decided_by}")
            print("[INFO] Executing action...")
            # Execute via MCP here

        elif status == ApprovalStatus.REJECTED:
            print(f"[REJECTED] Rejected by {decision.decided_by}")
            print(f"[REASON] {decision.comments}")

        else:  # EXPIRED
            print("[EXPIRED] Approval request timed out")

    else:
        print("[INFO] Action does not require approval, executing directly")


if __name__ == "__main__":
    main()
