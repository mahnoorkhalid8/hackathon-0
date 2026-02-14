# MCP Email Server - Quickstart Guide

Get the email server running in 5 minutes.

## Prerequisites

- Node.js v24+ installed
- SMTP credentials (Gmail, Outlook, etc.)

## Step 1: Install Dependencies (30 seconds)

```bash
cd mcp/email-server
npm install
```

## Step 2: Configure Environment (2 minutes)

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

**For Gmail (Recommended for Testing):**

1. Go to https://myaccount.google.com/apppasswords
2. Generate an App Password
3. Update `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_SECURE=false
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-email@gmail.com
```

## Step 3: Test Configuration (30 seconds)

```bash
npm test
```

Expected output:
```
✓ Valid email passes validation
✓ Missing required fields fails validation
...
✓ All tests passed!
```

## Step 4: Start Server (10 seconds)

```bash
npm start
```

Expected output:
```
2026-02-13 15:30:00 [info]: Starting MCP Email Server
2026-02-13 15:30:01 [info]: Email service initialized successfully
2026-02-13 15:30:01 [info]: MCP Email Server started successfully
```

## Step 5: Test from Python (1 minute)

Create `test_email.py`:

```python
import json
import subprocess

# Prepare email data
email_data = {
    "to": "recipient@example.com",
    "subject": "Test Email from MCP Server",
    "body": "This is a test email sent via MCP!"
}

# Call MCP server
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "send_email",
        "arguments": email_data
    }
}

# Send request via stdio
process = subprocess.Popen(
    ["node", "mcp/email-server/src/server.js"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = process.communicate(json.dumps(request))
result = json.loads(stdout)

print("Result:", result)
```

Run:
```bash
python test_email.py
```

## Done! 🎉

Your MCP email server is now running and ready to send emails.

## Next Steps

1. **Integrate with Digital FTE**: Add to `config/mcp_config.yaml`
2. **Configure Security**: Set domain filters in `.env`
3. **Monitor Logs**: `tail -f logs/email-server.log`
4. **Production Deploy**: See README.md for deployment options

## Common Issues

**"Missing credentials" error:**
- Check `.env` file exists and has correct values
- For Gmail, use App Password (not regular password)

**"Connection timeout":**
- Verify SMTP host and port
- Check firewall allows outbound connections

**"Authentication failed":**
- For Gmail: Enable 2FA and generate App Password
- Verify credentials are correct

## Quick Reference

```bash
# Start server
npm start

# Run tests
npm test

# View logs
tail -f logs/email-server.log

# Check configuration
cat .env
```

## Support

- Full documentation: `README.md`
- Configuration reference: `.env.example`
- Integration examples: `INTEGRATION_EXAMPLES.md`
