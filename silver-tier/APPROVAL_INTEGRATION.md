# Human-in-the-Loop Approval System - Integration Guide

## Overview

This guide shows how to integrate the approval system with your existing Digital FTE components.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Orchestrator → TaskRouter → Executor → MCP Client              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ ADD

┌─────────────────────────────────────────────────────────────────┐
│                 APPROVAL SYSTEM INTEGRATION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Orchestrator → TaskRouter → ApprovalManager → Executor         │
│                      ↓                ↓                          │
│                 Needs_Approval/   Monitor                        │
│                      ↓                ↓                          │
│                 Human Decision    Approved?                      │
│                                       ↓                          │
│                                   MCP Client                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Step 1: Install Dependencies

No additional dependencies required. The approval system uses only Python standard library.

```bash
# Verify Python 3.13+
python --version

# All dependencies already in requirements.txt
pip install -r requirements.txt
```

## Step 2: Add Configuration

Create or update `config/approval_rules.yaml`:

```yaml
# Approval Rules Configuration

# Actions that always require approval
sensitive_actions:
  - send_email
  - post_linkedin
  - post_twitter
  - external_api_call
  - delete_file
  - database_write
  - financial_transaction

# Actions that can be auto-approved (bypass human review)
auto_approve: []

# Actions that ALWAYS require approval (cannot be auto-approved)
always_require_approval:
  - financial_transaction
  - database_write
  - post_linkedin
  - post_twitter

# Timeout durations by priority (seconds)
timeout_by_priority:
  low: 7200      # 2 hours
  medium: 3600   # 1 hour
  high: 1800     # 30 minutes
  critical: 900  # 15 minutes

# Company email domains (for policy checks)
company_domains:
  - company.com
  - yourcompany.com

# Approval settings
approval_settings:
  poll_interval_seconds: 30
  default_timeout_seconds: 3600
  enable_notifications: true
  archive_after_days: 90
```

## Step 3: Update TaskRouter

Modify `core/task_router.py` to integrate approval checks:

```python
# core/task_router.py

from approval_system import ApprovalManager

class TaskRouter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # ... existing initialization ...

        # Initialize ApprovalManager
        self.approval_manager = ApprovalManager(config)

    def route_task(self, task: Dict[str, Any]) -> str:
        """
        Route task to appropriate queue.

        Returns:
            - "needs_approval" for sensitive actions
            - "execute_direct" for safe actions
            - "needs_action" for incomplete tasks
        """

        # Check if task is complete
        if not self._is_task_complete(task):
            return "needs_action"

        # Check if task requires approval
        if self.approval_manager.is_sensitive_action(task):
            return "needs_approval"

        # Safe to execute directly
        return "execute_direct"
```

## Step 4: Update Executor

Modify `core/executor.py` to handle approval workflow:

```python
# core/executor.py

from approval_system import ApprovalManager, ApprovalStatus

class Executor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # ... existing initialization ...

        # Initialize ApprovalManager
        self.approval_manager = ApprovalManager(config)

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with approval check.
        """

        # Check if approval is required
        if self.approval_manager.is_sensitive_action(task):
            return self._execute_with_approval(task)
        else:
            return self._execute_direct(task)

    def _execute_with_approval(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task after obtaining approval."""

        # Create approval request
        approval_id = self.approval_manager.create_approval_request(
            task=task,
            action_details=task.get("action_details", {})
        )

        self.logger.info(f"Approval request created: {approval_id}")

        # Monitor for decision
        timeout = self._get_timeout_for_priority(task.get("priority", "medium"))
        status, decision = self.approval_manager.monitor_approval(
            approval_id,
            timeout_seconds=timeout
        )

        if status == ApprovalStatus.APPROVED:
            # Execute the action
            result = self._execute_direct(task)

            # Archive as executed
            self.approval_manager._archive_approval(approval_id, "EXECUTED")

            return {
                "status": "success",
                "approval_id": approval_id,
                "result": result
            }

        elif status == ApprovalStatus.REJECTED:
            # Don't execute
            self.approval_manager._archive_approval(approval_id, "REJECTED")

            return {
                "status": "rejected",
                "approval_id": approval_id,
                "reason": decision.comments if decision else "No reason provided"
            }

        else:  # EXPIRED
            return {
                "status": "expired",
                "approval_id": approval_id,
                "reason": "Approval request timed out"
            }

    def _execute_direct(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task directly via MCP."""
        # ... existing execution logic ...
        pass

    def _get_timeout_for_priority(self, priority: str) -> int:
        """Get timeout duration based on priority."""
        timeouts = {
            "low": 7200,
            "medium": 3600,
            "high": 1800,
            "critical": 900
        }
        return timeouts.get(priority, 3600)
```

## Step 5: Update Orchestrator

Modify `core/orchestrator.py` to handle approval queue:

```python
# core/orchestrator.py

class Orchestrator:
    def __init__(self, config: Dict[str, Any]):
        # ... existing initialization ...

        # Add approval monitoring
        self.approval_queue = []

    def run(self):
        """Main orchestration loop."""

        while self.running:
            # ... existing logic ...

            # Process tasks
            for task in self.task_queue:
                # Route task
                route = self.task_router.route_task(task)

                if route == "needs_approval":
                    # Add to approval queue (non-blocking)
                    self.approval_queue.append(task)
                    self._start_approval_workflow(task)

                elif route == "execute_direct":
                    # Execute immediately
                    result = self.executor.execute(task)
                    self._handle_result(result)

                elif route == "needs_action":
                    # Move to Needs_Action
                    self._move_to_needs_action(task)

            # ... rest of loop ...

    def _start_approval_workflow(self, task: Dict[str, Any]):
        """Start approval workflow in background thread."""

        import threading

        def approval_thread():
            result = self.executor.execute(task)
            self._handle_result(result)

        thread = threading.Thread(target=approval_thread)
        thread.daemon = True
        thread.start()
```

## Step 6: Update Dashboard

Modify `core/state_manager.py` to show pending approvals:

```python
# core/state_manager.py

def update_dashboard(self):
    """Update Dashboard.md with current state."""

    # ... existing dashboard content ...

    # Add pending approvals section
    pending_approvals = self.approval_manager.get_pending_approvals()

    if pending_approvals:
        dashboard_content += "\n## Pending Approvals\n\n"
        dashboard_content += "| ID | Type | Priority | Created | Expires |\n"
        dashboard_content += "|----|------|----------|---------|----------|\n"

        for approval in pending_approvals:
            dashboard_content += (
                f"| {approval['id']} | "
                f"{approval['action_type']} | "
                f"{approval['priority']} | "
                f"{approval['created_at']} | "
                f"{approval['expires_at']} |\n"
            )

        dashboard_content += "\n**Action Required:** Review pending approvals in `vault/Needs_Approval/`\n"

    # Write dashboard
    with open("memory/Dashboard.md", 'w') as f:
        f.write(dashboard_content)
```

## Step 7: Test Integration

Run integration tests:

```bash
# Test approval system
python test_approval_system.py

# Run demo
python demo_approval_system.py

# Test full integration
python test_integration.py
```

## Step 8: Deploy

### Option A: Development Mode

```bash
# Run main system
python main.py
```

### Option B: Production Mode

```bash
# Run as systemd service (Linux)
sudo cp approval-watcher.service /etc/systemd/system/
sudo systemctl enable approval-watcher
sudo systemctl start approval-watcher

# Check status
sudo systemctl status approval-watcher
```

## Usage Examples

### Example 1: Send Email with Approval

```python
# Agent code
task = {
    "action_type": "send_email",
    "title": "Send weekly report",
    "priority": "high",
    "impact_level": "medium",
    "reversibility": "irreversible",
    "data_sensitivity": "low",
    "action_details": {
        "description": "Send weekly sales report to client",
        "mcp_server": "email_server",
        "method": "send_email",
        "parameters": {
            "to": "client@external.com",
            "subject": "Weekly Report",
            "body": "..."
        },
        "context": "Scheduled weekly report",
        "reasoning": "Client requested weekly updates",
        "expected_outcome": "Client receives report",
        "risks": [...],
        "safeguards": [...],
        "policy_status": "compliant"
    }
}

# Execute (will create approval request)
result = executor.execute(task)

# Result will be:
# - "pending" if waiting for approval
# - "success" if approved and executed
# - "rejected" if human rejected
# - "expired" if timeout occurred
```

### Example 2: Human Approval Process

```bash
# 1. Agent creates approval request
# File created: memory/Needs_Approval/APR-20260213-001.md

# 2. Human reviews file
cat memory/Needs_Approval/APR-20260213-001.md

# 3. Human approves by editing file
# Change: status: "PENDING" → status: "APPROVED"
# Add: decided_by: "John Doe"
# Save file

# 4. Agent detects approval (within 30 seconds)
# Executes action via MCP
# Archives to: memory/Done/APR-20260213-001-EXECUTED.md
```

## Monitoring and Debugging

### Check Pending Approvals

```python
from approval_system import ApprovalManager

manager = ApprovalManager(config)
pending = manager.get_pending_approvals()

for approval in pending:
    print(f"{approval['id']}: {approval['action_type']} ({approval['priority']})")
```

### View Logs

```bash
# Approval system logs
tail -f logs/approval_manager.log

# Executor logs
tail -f logs/executor.log

# Full system logs
tail -f logs/orchestrator.log
```

### Check Archived Approvals

```bash
# List all archived approvals
ls -lh memory/Done/APR-*.md

# View specific approval
cat memory/Done/APR-20260213-001-EXECUTED.md
```

## Troubleshooting

### Issue: Approval requests not being created

**Solution:**
1. Check if action is classified as sensitive
2. Verify `config/approval_rules.yaml` exists
3. Check logs: `logs/approval_manager.log`

### Issue: Agent not detecting human decisions

**Solution:**
1. Verify file format (YAML frontmatter)
2. Check status field: must be "APPROVED" or "REJECTED" (exact case)
3. Ensure file is saved properly
4. Check poll interval in config

### Issue: Approvals timing out too quickly

**Solution:**
1. Adjust timeout in `config/approval_rules.yaml`
2. Increase timeout for specific priority levels
3. Check system time synchronization

## Security Considerations

1. **File Permissions**: Ensure `memory/Needs_Approval/` is only writable by authorized users
2. **Audit Trail**: All approvals are logged with timestamps and approver names
3. **Policy Enforcement**: Approval rules are enforced at multiple levels
4. **Rollback**: All actions include rollback procedures where applicable

## Performance Impact

- **Memory**: ~10 MB per ApprovalManager instance
- **CPU**: Minimal (polling every 30 seconds)
- **Disk**: ~5 KB per approval request
- **Latency**: 0-30 seconds for approval detection (based on poll interval)

## Next Steps

1. Customize approval rules in `config/approval_rules.yaml`
2. Add custom policy checks in `approval_system.py`
3. Integrate with notification system (email, Slack, etc.)
4. Add approval analytics and reporting
5. Implement approval delegation (manager approval for high-value actions)

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review examples in `examples/` directory
- Run tests: `python test_approval_system.py`
- Run demo: `python demo_approval_system.py`
