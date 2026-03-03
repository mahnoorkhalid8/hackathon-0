"""
Demo: Human-in-the-Loop Approval System

This demo shows the complete approval workflow:
1. Agent detects sensitive action
2. Creates approval request
3. Monitors for human decision
4. Executes or rejects based on decision

Author: Digital FTE System
Date: 2026-02-13
"""

import os
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from approval_system import ApprovalManager, ApprovalStatus


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num: int, text: str):
    """Print formatted step."""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 70)


def demo_email_approval():
    """Demo: Email approval workflow."""
    print_header("Demo 1: Email Approval Workflow")

    # Initialize approval manager
    config = {
        "vault_path": "memory",
        "template_path": "templates",
        "poll_interval_seconds": 2,
        "default_timeout_seconds": 300,
        "company_domains": ["company.com"]
    }

    manager = ApprovalManager(config)

    print_step(1, "Agent receives task: Send weekly report to client")

    # Define email task
    email_task = {
        "action_type": "send_email",
        "title": "Send Weekly Sales Report",
        "priority": "high",
        "impact_level": "medium",
        "reversibility": "irreversible",
        "data_sensitivity": "low",
        "scope": "external",
        "requested_by": "agent",
        "recipients": ["client@external.com"]
    }

    print(f"  Task Type: {email_task['action_type']}")
    print(f"  Priority: {email_task['priority']}")
    print(f"  Recipient: {email_task['recipients'][0]}")

    print_step(2, "Agent checks if action requires approval")

    is_sensitive = manager.is_sensitive_action(email_task)
    print(f"  Sensitive Action: {is_sensitive}")

    if is_sensitive:
        print("  [OK] Action requires human approval")
    else:
        print("  [SKIP] Action can be executed directly")
        return

    print_step(3, "Agent creates approval request")

    action_details = {
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
            }
        ],
        "safeguards": [
            "Email content reviewed by data validation",
            "Recipient verified against CRM"
        ],
        "policy_status": "compliant",
        "preview_data": {
            "to": "client@external.com",
            "subject": "Weekly Sales Report - Week 7",
            "body": "Please find attached the weekly sales report..."
        }
    }

    approval_id = manager.create_approval_request(email_task, action_details)

    print(f"  [OK] Approval request created: {approval_id}")
    print(f"  [OK] File: memory/Needs_Approval/{approval_id}.md")

    print_step(4, "Human reviews and approves/rejects")

    print("  Waiting for human decision...")
    print("  (In real scenario, human would edit the file)")
    print()
    print("  To approve:")
    print(f"    1. Open: memory/Needs_Approval/{approval_id}.md")
    print("    2. Change: status: \"PENDING\" to status: \"APPROVED\"")
    print("    3. Save the file")
    print()
    print("  [INFO] Demo will auto-approve after 5 seconds...")

    # Simulate human approval after 5 seconds
    time.sleep(5)

    file_path = Path(f"memory/Needs_Approval/{approval_id}.md")
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('status: "PENDING"', 'status: "APPROVED"')
        content = content.replace('decided_by: "{{APPROVER_NAME}}"', 'decided_by: "demo_user"')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("  [OK] Demo auto-approved the request")

    print_step(5, "Agent detects approval and executes action")

    # Monitor for decision (short timeout for demo)
    status, decision = manager.monitor_approval(approval_id, timeout_seconds=10)

    if status == ApprovalStatus.APPROVED:
        print(f"  [OK] Approval granted by {decision.decided_by if decision else 'unknown'}")
        print("  [OK] Executing email send via MCP...")
        print("  [OK] Email sent successfully")

        # Archive
        manager._archive_approval(approval_id, "EXECUTED")
        print(f"  [OK] Archived to: memory/Done/{approval_id}-EXECUTED.md")

    elif status == ApprovalStatus.REJECTED:
        print(f"  [REJECTED] Approval rejected by {decision.decided_by if decision else 'unknown'}")
        print(f"  [REASON] {decision.comments if decision else 'No reason provided'}")

    else:
        print("  [EXPIRED] Approval request timed out")

    print("\n[OK] Demo 1 completed successfully!")


def demo_linkedin_approval():
    """Demo: LinkedIn post approval workflow."""
    print_header("Demo 2: LinkedIn Post Approval Workflow")

    config = {
        "vault_path": "memory",
        "template_path": "templates",
        "poll_interval_seconds": 2,
        "default_timeout_seconds": 300,
        "company_domains": ["company.com"]
    }

    manager = ApprovalManager(config)

    print_step(1, "Agent receives task: Post milestone to LinkedIn")

    linkedin_task = {
        "action_type": "post_linkedin",
        "title": "Post 10K Customers Milestone",
        "priority": "medium",
        "impact_level": "medium",
        "reversibility": "partially_reversible",
        "data_sensitivity": "none",
        "scope": "public",
        "requested_by": "agent"
    }

    print(f"  Task Type: {linkedin_task['action_type']}")
    print(f"  Priority: {linkedin_task['priority']}")
    print(f"  Scope: {linkedin_task['scope']}")

    print_step(2, "Agent checks if action requires approval")

    is_sensitive = manager.is_sensitive_action(linkedin_task)
    print(f"  Sensitive Action: {is_sensitive}")
    print("  [OK] Social media posts always require approval")

    print_step(3, "Agent creates approval request")

    action_details = {
        "description": "Post company milestone announcement to LinkedIn",
        "mcp_server": "social_media_server",
        "method": "post_to_linkedin",
        "parameters": {
            "account": "company_official",
            "content": "We've reached 10,000 customers! Thank you! 🎉",
            "visibility": "public"
        },
        "context": "Company reached 10K customers milestone today",
        "reasoning": "Marketing policy requires milestone announcements",
        "expected_outcome": "Positive brand visibility and engagement",
        "risks": [
            {
                "title": "Negative comments",
                "likelihood": "low",
                "impact": "medium",
                "mitigation": "Social media team monitors comments"
            }
        ],
        "safeguards": [
            "Content follows brand guidelines",
            "No sensitive business data disclosed"
        ],
        "policy_status": "compliant",
        "preview_data": {
            "content": "🎉 We've reached 10,000 customers! Thank you! 🎉"
        }
    }

    approval_id = manager.create_approval_request(linkedin_task, action_details)

    print(f"  [OK] Approval request created: {approval_id}")
    print(f"  [OK] File: memory/Needs_Approval/{approval_id}.md")

    print_step(4, "Simulating rejection scenario")

    print("  [INFO] Demo will auto-reject after 3 seconds...")
    time.sleep(3)

    file_path = Path(f"memory/Needs_Approval/{approval_id}.md")
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('status: "PENDING"', 'status: "REJECTED"')
        content = content.replace('decided_by: "{{APPROVER_NAME}}"', 'decided_by: "demo_user"')
        content = content.replace(
            'approval_comments: "{{APPROVAL_COMMENTS}}"',
            'approval_comments: "Marketing wants to review messaging first"'
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("  [OK] Demo auto-rejected the request")

    print_step(5, "Agent detects rejection and logs reason")

    status, decision = manager.monitor_approval(approval_id, timeout_seconds=10)

    if status == ApprovalStatus.REJECTED:
        print(f"  [REJECTED] Approval rejected by {decision.decided_by if decision else 'unknown'}")
        print(f"  [REASON] {decision.comments if decision else 'No reason provided'}")
        print("  [OK] Action NOT executed")

        # Archive
        manager._archive_approval(approval_id, "REJECTED")
        print(f"  [OK] Archived to: memory/Done/{approval_id}-REJECTED.md")

    print("\n[OK] Demo 2 completed successfully!")


def demo_timeout_scenario():
    """Demo: Timeout scenario."""
    print_header("Demo 3: Timeout Scenario")

    config = {
        "vault_path": "memory",
        "template_path": "templates",
        "poll_interval_seconds": 1,
        "default_timeout_seconds": 5,  # Very short timeout for demo
        "company_domains": ["company.com"]
    }

    manager = ApprovalManager(config)

    print_step(1, "Agent creates approval request with short timeout")

    task = {
        "action_type": "send_email",
        "title": "Test Email",
        "priority": "low",
        "impact_level": "low",
        "reversibility": "irreversible",
        "data_sensitivity": "none",
        "requested_by": "agent"
    }

    action_details = {
        "description": "Test email",
        "mcp_server": "email_server",
        "method": "send_email",
        "parameters": {"to": "test@example.com"},
        "context": "Test",
        "reasoning": "Test",
        "expected_outcome": "Test",
        "risks": [],
        "safeguards": [],
        "policy_status": "compliant"
    }

    approval_id = manager.create_approval_request(task, action_details)

    print(f"  [OK] Approval request created: {approval_id}")
    print(f"  [OK] Timeout set to: 5 seconds")

    print_step(2, "Agent monitors for decision (no human response)")

    print("  [INFO] Waiting for human decision...")
    print("  [INFO] (No human will respond - simulating timeout)")

    status, decision = manager.monitor_approval(approval_id, timeout_seconds=5)

    print_step(3, "Request expires due to timeout")

    if status == ApprovalStatus.EXPIRED:
        print("  [EXPIRED] Approval request timed out after 5 seconds")
        print("  [OK] Action NOT executed")
        print(f"  [OK] Archived to: memory/Done/{approval_id}-EXPIRED.md")

    print("\n[OK] Demo 3 completed successfully!")


def demo_pending_approvals_list():
    """Demo: List pending approvals."""
    print_header("Demo 4: List Pending Approvals")

    config = {
        "vault_path": "memory",
        "template_path": "templates",
        "poll_interval_seconds": 2,
        "default_timeout_seconds": 300,
        "company_domains": ["company.com"]
    }

    manager = ApprovalManager(config)

    print_step(1, "Create multiple approval requests")

    tasks = [
        {
            "action_type": "send_email",
            "title": "Email to Client A",
            "priority": "high"
        },
        {
            "action_type": "post_linkedin",
            "title": "LinkedIn Post",
            "priority": "medium"
        },
        {
            "action_type": "database_write",
            "title": "Database Migration",
            "priority": "critical"
        }
    ]

    action_details = {
        "description": "Test",
        "mcp_server": "test",
        "method": "test",
        "parameters": {},
        "context": "",
        "reasoning": "",
        "expected_outcome": "",
        "risks": [],
        "safeguards": [],
        "policy_status": "compliant"
    }

    for task in tasks:
        task.update({
            "impact_level": "medium",
            "reversibility": "irreversible",
            "data_sensitivity": "none",
            "requested_by": "agent"
        })
        approval_id = manager.create_approval_request(task, action_details)
        print(f"  [OK] Created: {approval_id} - {task['title']}")

    print_step(2, "Retrieve list of pending approvals")

    pending = manager.get_pending_approvals()

    print(f"\n  Found {len(pending)} pending approval(s):\n")

    for i, approval in enumerate(pending, 1):
        print(f"  {i}. ID: {approval['id']}")
        print(f"     Type: {approval['action_type']}")
        print(f"     Priority: {approval['priority']}")
        print(f"     Created: {approval['created_at']}")
        print()

    print("[OK] Demo 4 completed successfully!")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  Human-in-the-Loop Approval System - Interactive Demo")
    print("=" * 70)
    print("\n  This demo shows the complete approval workflow:")
    print("    1. Email approval (approved scenario)")
    print("    2. LinkedIn post (rejected scenario)")
    print("    3. Timeout scenario")
    print("    4. List pending approvals")
    print()

    try:
        # Run demos
        demo_email_approval()
        time.sleep(2)

        demo_linkedin_approval()
        time.sleep(2)

        demo_timeout_scenario()
        time.sleep(2)

        demo_pending_approvals_list()

        # Final summary
        print_header("Demo Complete")
        print("  All approval workflows demonstrated successfully!")
        print()
        print("  Key takeaways:")
        print("    - Sensitive actions are automatically detected")
        print("    - Approval requests are created in memory/Needs_Approval/")
        print("    - Humans edit files to approve/reject")
        print("    - Agent monitors files and executes accordingly")
        print("    - Completed requests are archived to memory/Done/")
        print()
        print("  Next steps:")
        print("    1. Review approval files in memory/Needs_Approval/")
        print("    2. Check archived files in memory/Done/")
        print("    3. Run tests: python test_approval_system.py")
        print("    4. Integrate with your Digital FTE system")
        print()

    except KeyboardInterrupt:
        print("\n\n[INFO] Demo interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
