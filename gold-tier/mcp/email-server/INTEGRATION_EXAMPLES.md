# MCP Email Server - Integration Examples

Complete examples for integrating the email server with Digital FTE components.

## Example 1: Basic Email Sending

### Python Integration

```python
"""
Basic email sending via MCP server
"""

from mcp.mcp_client import MCPClient

# Initialize MCP client
mcp = MCPClient()

# Send email
result = mcp.execute(
    server="email_server",
    method="send_email",
    parameters={
        "to": "client@example.com",
        "subject": "Weekly Sales Report",
        "body": "Please find the weekly sales report attached."
    }
)

if result["success"]:
    print(f"✓ Email sent successfully")
    print(f"  Message ID: {result['messageId']}")
    print(f"  Duration: {result['duration']}ms")
else:
    print(f"✗ Failed to send email: {result['error']}")
```

## Example 2: Email with CC and BCC

```python
"""
Send email with CC and BCC recipients
"""

result = mcp.execute(
    server="email_server",
    method="send_email",
    parameters={
        "to": "primary@example.com",
        "cc": ["manager@company.com", "team@company.com"],
        "bcc": "archive@company.com",
        "subject": "Project Update",
        "body": "Here's the latest project update..."
    }
)
```

## Example 3: HTML Email

```python
"""
Send HTML formatted email
"""

html_body = """
<html>
<body>
    <h1>Weekly Report</h1>
    <p>Dear Client,</p>
    <p>Here are this week's highlights:</p>
    <ul>
        <li>Sales: $127,450 (↑12%)</li>
        <li>New customers: 23</li>
        <li>Satisfaction: 4.8/5.0</li>
    </ul>
    <p>Best regards,<br>Your Team</p>
</body>
</html>
"""

result = mcp.execute(
    server="email_server",
    method="send_email",
    parameters={
        "to": "client@example.com",
        "subject": "Weekly Report - Week 7",
        "body": html_body
    }
)
```

## Example 4: Batch Email Sending

```python
"""
Send multiple emails in batch
"""

emails = [
    {
        "to": "client1@example.com",
        "subject": "Invoice #1001",
        "body": "Your invoice is ready..."
    },
    {
        "to": "client2@example.com",
        "subject": "Invoice #1002",
        "body": "Your invoice is ready..."
    },
    {
        "to": "client3@example.com",
        "subject": "Invoice #1003",
        "body": "Your invoice is ready..."
    }
]

result = mcp.execute(
    server="email_server",
    method="send_batch_emails",
    parameters={"emails": emails}
)

print(f"Sent {result['successCount']}/{result['total']} emails")
```

## Example 5: Integration with Approval System

```python
"""
Send email with human approval workflow
"""

from approval_system import ApprovalManager, ApprovalStatus

# Initialize approval manager
approval_manager = ApprovalManager(config)

# Define email task
email_task = {
    "action_type": "send_email",
    "title": "Send weekly report to client",
    "priority": "high",
    "impact_level": "medium",
    "reversibility": "irreversible",
    "data_sensitivity": "low",
    "scope": "external",
    "requested_by": "agent"
}

# Define action details
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

# Create approval request
approval_id = approval_manager.create_approval_request(
    task=email_task,
    action_details=action_details
)

print(f"Approval request created: {approval_id}")
print(f"File: memory/Needs_Approval/{approval_id}.md")

# Monitor for approval
status, decision = approval_manager.monitor_approval(approval_id)

if status == ApprovalStatus.APPROVED:
    # Execute email send
    result = mcp.execute(
        server=action_details["mcp_server"],
        method=action_details["method"],
        parameters=action_details["parameters"]
    )

    if result["success"]:
        print(f"✓ Email sent: {result['messageId']}")
        approval_manager._archive_approval(approval_id, "EXECUTED")
    else:
        print(f"✗ Failed: {result['error']}")
        approval_manager._archive_approval(approval_id, "FAILED")
else:
    print(f"✗ Approval {status.value}")
```

## Example 6: Integration with Executor

```python
"""
Integrate email server with Digital FTE Executor
"""

from core.executor import Executor

class EmailExecutor(Executor):
    def execute_email_action(self, task):
        """Execute email action via MCP"""

        # Validate task
        if not self._validate_email_task(task):
            return {
                "status": "error",
                "error": "Invalid email task"
            }

        # Send via MCP
        result = self.mcp_client.execute(
            server="email_server",
            method="send_email",
            parameters=task["parameters"]
        )

        # Log result
        self.logger.info("Email action executed", {
            "success": result["success"],
            "messageId": result.get("messageId"),
            "to": task["parameters"]["to"]
        })

        return result

    def _validate_email_task(self, task):
        """Validate email task structure"""
        required = ["to", "subject", "body"]
        return all(k in task.get("parameters", {}) for k in required)
```

## Example 7: Error Handling

```python
"""
Robust error handling for email operations
"""

import time

def send_email_with_retry(mcp, email_data, max_retries=3):
    """Send email with automatic retry on failure"""

    for attempt in range(max_retries):
        try:
            result = mcp.execute(
                server="email_server",
                method="send_email",
                parameters=email_data
            )

            if result["success"]:
                return result

            # Check if rate limited
            if "retryAfter" in result:
                wait_time = result["retryAfter"]
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            # Other error
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return result

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Exception: {e}, retrying...")
                time.sleep(2 ** attempt)
            else:
                return {
                    "success": False,
                    "error": str(e)
                }

    return {
        "success": False,
        "error": "Max retries exceeded"
    }

# Usage
result = send_email_with_retry(mcp, {
    "to": "client@example.com",
    "subject": "Important Update",
    "body": "This is an important update..."
})
```

## Example 8: Email Templates

```python
"""
Use email templates for consistent formatting
"""

class EmailTemplates:
    @staticmethod
    def weekly_report(data):
        """Generate weekly report email"""
        return {
            "subject": f"Weekly Report - Week {data['week']}",
            "body": f"""
Dear {data['recipient_name']},

Here's your weekly report for Week {data['week']}:

Sales Performance:
- Total Sales: ${data['total_sales']:,.2f}
- Growth: {data['growth_percent']}%
- New Customers: {data['new_customers']}

Customer Satisfaction:
- Average Rating: {data['satisfaction']}/5.0
- Response Rate: {data['response_rate']}%

Best regards,
{data['sender_name']}
            """.strip()
        }

    @staticmethod
    def invoice(data):
        """Generate invoice email"""
        return {
            "subject": f"Invoice #{data['invoice_number']}",
            "body": f"""
Dear {data['customer_name']},

Your invoice is ready.

Invoice Number: {data['invoice_number']}
Amount Due: ${data['amount']:,.2f}
Due Date: {data['due_date']}

Please find the invoice attached.

Thank you for your business!
            """.strip()
        }

# Usage
email_data = EmailTemplates.weekly_report({
    "week": 7,
    "recipient_name": "Sarah Johnson",
    "total_sales": 127450,
    "growth_percent": 12,
    "new_customers": 23,
    "satisfaction": 4.8,
    "response_rate": 87,
    "sender_name": "Digital FTE"
})

result = mcp.execute(
    server="email_server",
    method="send_email",
    parameters={
        "to": "client@example.com",
        **email_data
    }
)
```

## Example 9: Scheduled Email Sending

```python
"""
Schedule emails using time watcher
"""

from scheduler.scheduler import Scheduler

# Define scheduled email task
scheduled_task = {
    "name": "weekly_report_email",
    "schedule": "0 9 * * MON",  # Every Monday at 9 AM
    "action": {
        "type": "send_email",
        "mcp_server": "email_server",
        "method": "send_email",
        "parameters": {
            "to": "client@example.com",
            "subject": "Weekly Report",
            "body": "Your weekly report is ready..."
        }
    }
}

# Add to scheduler
scheduler = Scheduler()
scheduler.add_task(scheduled_task)
```

## Example 10: Email Monitoring and Logging

```python
"""
Monitor email operations and log metrics
"""

class EmailMonitor:
    def __init__(self):
        self.sent_count = 0
        self.failed_count = 0
        self.total_duration = 0

    def send_and_monitor(self, mcp, email_data):
        """Send email and track metrics"""

        start_time = time.time()

        result = mcp.execute(
            server="email_server",
            method="send_email",
            parameters=email_data
        )

        duration = (time.time() - start_time) * 1000

        if result["success"]:
            self.sent_count += 1
            self.total_duration += duration

            self.logger.info("Email sent", {
                "to": email_data["to"],
                "messageId": result["messageId"],
                "duration": f"{duration:.0f}ms"
            })
        else:
            self.failed_count += 1

            self.logger.error("Email failed", {
                "to": email_data["to"],
                "error": result["error"]
            })

        return result

    def get_stats(self):
        """Get email statistics"""
        avg_duration = (
            self.total_duration / self.sent_count
            if self.sent_count > 0
            else 0
        )

        return {
            "sent": self.sent_count,
            "failed": self.failed_count,
            "success_rate": (
                self.sent_count / (self.sent_count + self.failed_count) * 100
                if (self.sent_count + self.failed_count) > 0
                else 0
            ),
            "avg_duration": f"{avg_duration:.0f}ms"
        }

# Usage
monitor = EmailMonitor()

for email in email_list:
    monitor.send_and_monitor(mcp, email)

print("Email Statistics:", monitor.get_stats())
```

## Configuration in mcp_config.yaml

```yaml
# MCP Server Configuration
servers:
  email_server:
    command: node
    args:
      - mcp/email-server/src/server.js
    env:
      NODE_ENV: production
      LOG_LEVEL: info
    description: "Email sending via SMTP"
    enabled: true
```

## Testing Integration

```python
"""
Test MCP email server integration
"""

def test_email_integration():
    """Test email server is working"""

    # Test connection
    result = mcp.execute(
        server="email_server",
        method="test_email_connection",
        parameters={}
    )

    assert result["success"], "Email server connection failed"
    print("✓ Email server connection successful")

    # Test email sending (to yourself)
    result = mcp.execute(
        server="email_server",
        method="send_email",
        parameters={
            "to": "your-email@example.com",
            "subject": "Test Email",
            "body": "This is a test email from MCP server"
        }
    )

    assert result["success"], f"Email send failed: {result.get('error')}"
    print(f"✓ Test email sent: {result['messageId']}")

if __name__ == "__main__":
    test_email_integration()
```

## Best Practices

1. **Always validate email data** before sending
2. **Use templates** for consistent formatting
3. **Implement retry logic** for transient failures
4. **Monitor and log** all email operations
5. **Handle rate limits** gracefully
6. **Use approval workflow** for external emails
7. **Test thoroughly** before production use
8. **Keep credentials secure** (never commit .env)

## Support

For more examples and documentation:
- Main README: `README.md`
- Quickstart: `QUICKSTART.md`
- API Reference: See MCP server logs
