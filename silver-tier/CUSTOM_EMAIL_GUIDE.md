# Custom Email Sending Guide

## Overview

This guide explains how to send custom formal emails using the Silver Tier Digital FTE system with **Gmail API**.

## Two Email Systems

### 1. CEO Briefing (Automated)

**Command:** `python run_agent.py ceo-report`

**Purpose:** Automatically generates and sends Monday Morning CEO Briefing with task analysis, metrics, and recommendations.

**Template:** `templates/monday-briefing-template.md`

**Recipient:** khalidmahnoor889@gmail.com (set via `CEO_EMAIL` in `.env`)

**When to use:** Automated weekly executive reporting

---

### 2. Custom Formal Emails (Manual)

**Command:** `python send_custom_email.py`

**Purpose:** Send custom formal emails to any recipient with your own content.

**Template:** `templates/formal-email-template.md`

**Recipient:** Specified at runtime

**When to use:** One-off formal communications, business correspondence

---

## Quick Start: Sending Custom Emails

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Gmail API libraries (google-auth, google-api-python-client)
- Other required packages

### Step 2: Configure Gmail API

You need two files from Google Cloud:

1. **credentials.json** - OAuth2 credentials from Google Cloud Console
2. **token.json** - Auto-generated on first run

See **GMAIL_API_SETUP.md** for detailed setup instructions.

Quick setup:
```bash
# 1. Place credentials.json in project root
# 2. Run this command (will open browser for authentication)
python run_agent.py ceo-report
# 3. Sign in and grant permissions
# 4. token.json will be created automatically
```

### Step 3: Send Email (Interactive Mode)

```bash
python send_custom_email.py
```

You'll be prompted for:
- Recipient email
- Subject
- Recipient name
- Opening paragraph
- Main body
- Closing paragraph

### Step 4: Send Email (Command Line)

```bash
python send_custom_email.py recipient@example.com
```

Then provide the remaining details when prompted.

---

## Email Template Customization

### Template Location

`templates/formal-email-template.md`

### Template Structure

```markdown
Dear {{RECIPIENT_NAME}},

{{OPENING_PARAGRAPH}}

{{MAIN_BODY}}

{{CLOSING_PARAGRAPH}}

Best regards,
{{SENDER_NAME}}
{{SENDER_TITLE}}
{{COMPANY_NAME}}
```

### Available Placeholders

- `{{RECIPIENT_NAME}}` - Name of the recipient
- `{{OPENING_PARAGRAPH}}` - Opening greeting/context
- `{{MAIN_BODY}}` - Main content of the email
- `{{CLOSING_PARAGRAPH}}` - Closing remarks
- `{{SENDER_NAME}}` - Your name or system name
- `{{SENDER_TITLE}}` - Your title
- `{{COMPANY_NAME}}` - Your company name

### Customizing the Template

Edit `templates/formal-email-template.md` to change:
- Greeting style (Dear/Hello/Hi)
- Signature format
- Additional sections
- Formatting

Example custom template:

```markdown
Hello {{RECIPIENT_NAME}},

{{OPENING_PARAGRAPH}}

## Details

{{MAIN_BODY}}

## Next Steps

{{CLOSING_PARAGRAPH}}

Warm regards,

{{SENDER_NAME}}
{{SENDER_TITLE}}
{{COMPANY_NAME}}
Email: contact@company.com
Phone: +1-555-0100
```

---

## Programmatic Usage

### Python Script Example

```python
from send_custom_email import CustomEmailSender

# Initialize sender
sender = CustomEmailSender()

# Send formal email
result = sender.send_formal_email(
    to="client@example.com",
    subject="Project Update - Q1 2026",
    recipient_name="John Smith",
    opening="I hope this email finds you well. I wanted to provide you with an update on our Q1 progress.",
    main_body="""
We have successfully completed the following milestones:

1. Digital FTE System - Core functionality deployed
2. Email Integration - MCP server operational
3. Approval Workflow - Human-in-the-loop system active
4. CEO Briefing - Automated weekly reports

All systems are running smoothly and meeting performance targets.
    """,
    closing="Please let me know if you have any questions or would like to schedule a call to discuss further.",
    sender_name="Digital FTE Team",
    sender_title="Project Manager",
    company_name="Your Company"
)

# Check result
if result["success"]:
    print(f"Email sent successfully at {result['timestamp']}")
else:
    print(f"Failed to send email: {result['error']}")
```

### Integration with Existing Code

```python
# In your existing Python scripts
from send_custom_email import CustomEmailSender

def notify_stakeholder(email, message):
    sender = CustomEmailSender()
    result = sender.send_formal_email(
        to=email,
        subject="Notification from Digital FTE",
        recipient_name="Stakeholder",
        opening="This is an automated notification from the Digital FTE system.",
        main_body=message,
        closing="This is an automated message. Please do not reply directly to this email.",
        sender_name="Digital FTE System",
        sender_title="Automated Agent",
        company_name="Your Organization"
    )
    return result["success"]
```

---

## Common Use Cases

### 1. Client Communication

```bash
python send_custom_email.py client@example.com
Subject: Project Status Update
Recipient name: Sarah Johnson
Opening: I hope you're doing well. I wanted to share our latest progress.
Main body: We've completed phases 1-3 ahead of schedule...
Closing: Looking forward to our meeting next week.
```

### 2. Team Notifications

```python
sender = CustomEmailSender()
for team_member in team_emails:
    sender.send_formal_email(
        to=team_member,
        subject="Weekly Team Update",
        recipient_name="Team Member",
        opening="Here's your weekly update.",
        main_body=weekly_summary,
        closing="Have a great week!",
        sender_name="Team Lead",
        sender_title="Project Manager",
        company_name="Your Company"
    )
```

### 3. Approval Notifications

```python
# After approval is granted
sender = CustomEmailSender()
sender.send_formal_email(
    to=requester_email,
    subject="Approval Granted - Action Authorized",
    recipient_name=requester_name,
    opening="Your request has been reviewed and approved.",
    main_body=f"Action: {action_description}\nApproved by: {approver}\nTimestamp: {timestamp}",
    closing="You may proceed with the authorized action.",
    sender_name="Approval System",
    sender_title="Digital FTE",
    company_name="Your Organization"
)
```

---

## Troubleshooting

### Issue: "Template not found"

**Solution:**
```bash
# Check template exists
ls templates/formal-email-template.md

# If missing, create it
python send_custom_email.py
# Will show error with expected path
```

### Issue: "Failed to send email"

**Solution:**
1. Check MCP email server is configured:
   ```bash
   cd mcp/email-server
   cat .env
   ```

2. Verify SMTP credentials are correct

3. Check email server logs:
   ```bash
   tail -f mcp/email-server/logs/email-server.log
   ```

### Issue: "Module not found"

**Solution:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd mcp/email-server
npm install
```

---

## Security Best Practices

1. **Never hardcode credentials** - Always use `.env` file
2. **Use App Passwords** - For Gmail, use app-specific passwords
3. **Validate recipients** - Check email addresses before sending
4. **Rate limiting** - MCP server has built-in rate limiting (10 emails/minute)
5. **Log all sends** - All emails are logged for audit trail

---

## Comparison: CEO Briefing vs Custom Email

| Feature | CEO Briefing | Custom Email |
|---------|-------------|--------------|
| Command | `python run_agent.py ceo-report` | `python send_custom_email.py` |
| Content | Auto-generated from task analysis | User-provided |
| Template | `monday-briefing-template.md` | `formal-email-template.md` |
| Recipient | CEO_EMAIL (env var) | Specified at runtime |
| Schedule | Automated (Monday 9AM) | Manual/on-demand |
| Use Case | Weekly executive reporting | Custom business communication |

---

## Next Steps

1. **Test the system:**
   ```bash
   python send_custom_email.py your-email@example.com
   ```

2. **Customize the template** to match your organization's style

3. **Integrate with your workflows** using the Python API

4. **Set up monitoring** to track email delivery

---

## Support

For issues or questions:
- Check logs: `mcp/email-server/logs/email-server.log`
- Review MCP server status: `cd mcp/email-server && npm start`
- Test SMTP connection: Use the `test_email_connection` MCP tool

---

**Last Updated:** 2026-02-14
**Version:** 1.0.0
