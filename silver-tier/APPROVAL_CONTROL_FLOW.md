# Human-in-the-Loop Approval System - Control Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT EXECUTION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. Task Received
   │
   ├─→ [Task Router] Analyze task
   │
   ├─→ Is Sensitive Action?
   │   │
   │   ├─→ NO: Execute directly via Executor
   │   │   └─→ Log to vault/Done/
   │   │
   │   └─→ YES: Route to Approval Workflow
   │       │
   │       ├─→ [Approval Manager] Create approval request
   │       │   └─→ Generate approval file in vault/Needs_Approval/
   │       │
   │       ├─→ [Approval Monitor] Poll for decision (every 30s)
   │       │   │
   │       │   ├─→ Status = PENDING
   │       │   │   └─→ Continue monitoring (check expiry)
   │       │   │
   │       │   ├─→ Status = APPROVED
   │       │   │   ├─ [Executor] Execute action via MCP
   │       │   │   ├─→ Log execution result
   │       │   │   └─→ Move to vault/Done/
   │       │   │
   │       │   ├─→ Status = REJECTED
   │       │   │   ├─→ Log rejection reason
   │       │   │   ├─→ Move to vault/Done/
   │       │   │   └─→ Continue with next task
   │       │   │
   │       │   └─→ Status = EXPIRED
   │       │       ├─→ Auto-reject (timeout reached)
   │       │       ├─→ Move to vault/Done/
   │       │       └─→ Continue with next task
   │       │
   │       └─→ [State Manager] Update Dashboard.md
   │
   └─→ Next Task

```

## Sensitive Action Detection

```
┌─────────────────────────────────────────────────────────────────┐
│                  SENSITIVITY CLASSIFICATION                      │
└─────────────────────────────────────────────────────────────────┘

Action Type          | Requires Approval | Reason
---------------------|-------------------|---------------------------
Send Email           | YES               | External communication
LinkedIn Post        | YES               | Public visibility
Twitter Post         | YES               | Public visibility
API Call (external)  | YES               | External system impact
File Delete          | CONDITIONAL       | If size > 10MB or critical
Database Write       | CONDITIONAL       | If production DB
Financial Action     | YES               | Monetary impact
User Data Access     | YES               | Privacy/compliance
System Config Change | CONDITIONAL       | If production system
Read-only Query      | NO                | No side effects
Internal Logging     | NO                | Safe operation
File Read            | NO                | Safe operation

```

## Approval Request Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPROVAL STATE MACHINE                        │
└─────────────────────────────────────────────────────────────────┘

    [CREATED]
        │
        ├─→ Write to vault/Needs_Approval/
        │
        ▼
    [PENDING]
        │
        ├─→ Monitor every 30s
        │   │
        │   ├─→ Human changes status to APPROVED
        │   │   │
        │   │   ▼
        │   [APPROVED]
        │   │   │
        │   │   ├─→ Execute action
        │   │   ├─→ Log result
        │   │   └─→ Move to vault/Done/
        │   │
        │   ├─→ Human changes status to REJECTED
        │   │   │
        │   │   ▼
        │   [REJECTED]
        │   │   │
        │   │   ├─→ Log rejection
        │   │   └─→ Move to vault/Done/
        │   │
        │   └─→ Timeout reached (no human response)
        │       │
        │       ▼
        │   [EXPIRED]
        │       │
        │       ├─→ Auto-reject
        │       └─→ Move to vault/Done/
        │
        └─→ [TERMINAL STATE]

```

## Integration Points

### 1. Task Router Integration

```python
# core/task_router.py

def route_task(task: Dict[str, Any]) -> str:
    """
    Routes task to appropriate queue based on sensitivity.

    Returns:
        - "execute_direct" for non-sensitive actions
        - "needs_approval" for sensitive actions
        - "needs_action" for tasks requiring more info
    """

    if is_sensitive_action(task):
        return "needs_approval"
    elif is_ready_to_execute(task):
        return "execute_direct"
    else:
        return "needs_action"

def is_sensitive_action(task: Dict[str, Any]) -> bool:
    """
    Determines if task requires human approval.

    Checks:
        - Action type (email, social media, external API)
        - Impact level (high/critical)
        - Data sensitivity (PII, financial)
        - Reversibility (irreversible actions)
        - Company policy rules
    """

    sensitive_types = [
        "send_email",
        "post_linkedin",
        "post_twitter",
        "external_api_call",
        "delete_file",
        "database_write",
        "financial_transaction"
    ]

    action_type = task.get("action_type", "")
    impact_level = task.get("impact_level", "low")
    data_sensitivity = task.get("data_sensitivity", "none")
    reversibility = task.get("reversibility", "reversible")

    # Check action type
    if action_type in sensitive_types:
        return True

    # Check impact and sensitivity
    if impact_level in ["high", "critical"]:
        return True

    if data_sensitivity in ["high", "pii"]:
        return True

    if reversibility == "irreversible":
        return True

    # Check company policy
    if violates_policy(task):
        return True

    return False
```

### 2. Approval Manager Integration

```python
# core/approval_manager.py

class ApprovalManager:
    """
    Manages creation and monitoring of approval requests.
    """

    def create_approval_request(
        self,
        task: Dict[str, Any],
        action_details: Dict[str, Any]
    ) -> str:
        """
        Creates approval request file in vault/Needs_Approval/.

        Returns:
            approval_id: Unique identifier for tracking
        """

        approval_id = generate_approval_id()
        approval_file = self._generate_approval_file(
            approval_id,
            task,
            action_details
        )

        file_path = f"vault/Needs_Approval/{approval_id}.md"
        write_file(file_path, approval_file)

        self.logger.info(f"Approval request created: {approval_id}")
        return approval_id

    def monitor_approval(
        self,
        approval_id: str,
        timeout_seconds: int = 3600
    ) -> str:
        """
        Monitors approval request until decision or timeout.

        Returns:
            status: "APPROVED" | "REJECTED" | "EXPIRED"
        """

        start_time = time.time()
        file_path = f"vault/Needs_Approval/{approval_id}.md"

        while True:
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                self._mark_expired(approval_id)
                return "EXPIRED"

            # Read current status
            status = self._read_approval_status(file_path)

            if status == "APPROVED":
                self.logger.info(f"Approval granted: {approval_id}")
                return "APPROVED"

            elif status == "REJECTED":
                self.logger.info(f"Approval rejected: {approval_id}")
                return "REJECTED"

            # Still pending, wait and check again
            time.sleep(30)  # Poll every 30 seconds
```

### 3. Executor Integration

```python
# core/executor.py

def execute_with_approval(
    self,
    task: Dict[str, Any],
    approval_id: str
) -> Dict[str, Any]:
    """
    Executes approved action via MCP server.

    Only called after approval is granted.
    """

    try:
        # Verify approval status one more time
        if not self._verify_approved(approval_id):
            raise ApprovalError("Approval status changed before execution")

        # Execute via MCP
        result = self.mcp_client.execute(
            server=task["mcp_server"],
            method=task["method"],
            parameters=task["parameters"]
        )

        # Log execution
        self._log_execution(approval_id, result)

        # Move approval file to Done
        self._archive_approval(approval_id, "EXECUTED")

        return {
            "status": "success",
            "approval_id": approval_id,
            "result": result
        }

    except Exception as e:
        self.logger.error(f"Execution failed: {e}")
        self._archive_approval(approval_id, "FAILED")
        raise
```

## File System Layout

```
vault/
├── Needs_Approval/          # Pending approval requests
│   ├── APR-20260213-001.md  # Email approval request
│   ├── APR-20260213-002.md  # LinkedIn post approval
│   └── APR-20260213-003.md  # API call approval
│
├── Done/                    # Completed actions
│   ├── APR-20260213-001-APPROVED-EXECUTED.md
│   ├── APR-20260213-002-REJECTED.md
│   └── APR-20260213-003-EXPIRED.md
│
└── Dashboard.md             # Shows pending approvals count

```

## Dashboard Integration

```markdown
# Digital FTE Dashboard

## Pending Approvals (3)

| ID | Type | Priority | Created | Expires |
|----|------|----------|---------|---------|
| APR-001 | Email | High | 10:30 AM | 11:30 AM |
| APR-002 | LinkedIn | Medium | 10:45 AM | 12:45 PM |
| APR-003 | API Call | Critical | 11:00 AM | 12:00 PM |

**Action Required:** Review pending approvals in vault/Needs_Approval/
```

## Notification System

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION TRIGGERS                         │
└─────────────────────────────────────────────────────────────────┘

Event                    | Notification Method
-------------------------|----------------------------------
Approval Created         | Update Dashboard.md
Approval Pending > 30min | Email reminder to human
Approval Approved        | Log to execution log
Approval Rejected        | Log rejection reason
Approval Expired         | Email notification + log
Execution Completed      | Update Dashboard.md + log
Execution Failed         | Email alert + error log

```

## Security & Compliance

### Audit Trail

Every approval request maintains complete audit trail:
- Who requested the action (agent)
- When it was requested
- What was the proposed action
- Risk analysis performed
- Who approved/rejected (human)
- When decision was made
- Execution result (if approved)
- Any errors or failures

### Policy Enforcement

```python
def check_policy_compliance(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks task against company policies.

    Returns:
        {
            "compliant": bool,
            "violations": List[str],
            "warnings": List[str],
            "required_approvals": List[str]
        }
    """

    violations = []
    warnings = []
    required_approvals = []

    # Check email policies
    if task["action_type"] == "send_email":
        if contains_sensitive_data(task["content"]):
            violations.append("Email contains PII without encryption")
        if external_recipient(task["to"]):
            required_approvals.append("manager")

    # Check social media policies
    if task["action_type"] in ["post_linkedin", "post_twitter"]:
        if not reviewed_by_marketing(task):
            warnings.append("Marketing review recommended")
        required_approvals.append("human")

    # Check financial policies
    if task["action_type"] == "financial_transaction":
        if task["amount"] > 1000:
            required_approvals.append("manager")
        if task["amount"] > 10000:
            required_approvals.append("legal")

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "required_approvals": required_approvals
    }
```
