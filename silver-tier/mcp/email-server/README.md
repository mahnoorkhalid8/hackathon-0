# MCP Email Server for Silver Tier Digital FTE

A production-ready Model Context Protocol (MCP) server for email functionality built with Node.js v24. Provides secure, rate-limited email sending with comprehensive validation, logging, and error handling.

## Features

✅ **MCP Protocol Integration** - Full MCP SDK implementation with stdio transport
✅ **Email Sending** - SMTP email delivery using nodemailer
✅ **Batch Support** - Send multiple emails efficiently
✅ **Comprehensive Validation** - Joi-based schema validation with security checks
✅ **Rate Limiting** - Token bucket algorithm prevents abuse
✅ **Security** - Domain filtering, content scanning, size limits
✅ **Logging** - Structured logging with Winston (file + console)
✅ **Error Handling** - Graceful error handling with detailed error messages
✅ **Production Ready** - Modular architecture, configuration management, testing

## Architecture

```
mcp/email-server/
├── src/
│   ├── server.js                 # Main MCP server
│   ├── services/
│   │   └── emailService.js       # Email sending logic
│   ├── config/
│   │   └── config.js             # Configuration management
│   └── utils/
│       ├── logger.js             # Winston logging
│       ├── validator.js          # Joi validation
│       └── rateLimiter.js        # Rate limiting
├── logs/                         # Log files
├── .env                          # Environment configuration
├── .env.example                  # Environment template
├── package.json                  # Dependencies
└── README.md                     # This file
```

## Requirements

- **Node.js**: v24.0.0 or higher
- **SMTP Server**: Gmail, Outlook, SendGrid, or any SMTP provider
- **Python**: 3.13+ (for Digital FTE integration)

## Installation

### 1. Install Dependencies

```bash
cd mcp/email-server
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your SMTP credentials:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_SECURE=false
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password)

**For Other Providers:**
- **Outlook**: `smtp-mail.outlook.com:587`
- **SendGrid**: `smtp.sendgrid.net:587` (use API key as password)
- **AWS SES**: `email-smtp.us-east-1.amazonaws.com:587`

### 3. Test Configuration

```bash
npm test
```

## Usage

### Starting the Server

```bash
# Production mode
npm start

# Development mode (with auto-reload)
npm run dev
```

### Available Tools

The MCP server provides three tools:

#### 1. send_email

Send a single email.

**Input:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content (plain text or HTML)",
  "from": "sender@example.com",
  "cc": "cc@example.com",
  "bcc": ["bcc1@example.com", "bcc2@example.com"]
}
```

**Output:**
```json
{
  "success": true,
  "messageId": "<unique-message-id>",
  "response": "250 Message accepted",
  "duration": 1234,
  "requestId": "email-1234567890-abc123",
  "rateLimitRemaining": 59
}
```

#### 2. send_batch_emails

Send multiple emails in batch.

**Input:**
```json
{
  "emails": [
    {
      "to": "recipient1@example.com",
      "subject": "Subject 1",
      "body": "Body 1"
    },
    {
      "to": "recipient2@example.com",
      "subject": "Subject 2",
      "body": "Body 2"
    }
  ]
}
```

**Output:**
```json
{
  "success": true,
  "total": 2,
  "successCount": 2,
  "failureCount": 0,
  "results": [...]
}
```

#### 3. test_email_connection

Test SMTP server connection.

**Input:**
```json
{}
```

**Output:**
```json
{
  "success": true,
  "message": "Email server connection successful",
  "config": {
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": false,
    "user": "your-email@gmail.com"
  }
}
```

## Integration with Digital FTE

### 1. Add to MCP Configuration

Edit `config/mcp_config.yaml`:

```yaml
servers:
  email_server:
    command: node
    args:
      - mcp/email-server/src/server.js
    env:
      NODE_ENV: production
```

### 2. Use in Python

```python
from mcp.mcp_client import MCPClient

# Initialize MCP client
mcp_client = MCPClient()

# Send email
result = mcp_client.execute(
    server="email_server",
    method="send_email",
    parameters={
        "to": "client@example.com",
        "subject": "Weekly Report",
        "body": "Please find attached the weekly report..."
    }
)

if result["success"]:
    print(f"Email sent: {result['messageId']}")
else:
    print(f"Failed: {result['error']}")
```

### 3. Use with Approval System

```python
# In approval_system.py
action_details = {
    "mcp_server": "email_server",
    "method": "send_email",
    "parameters": {
        "to": "client@external.com",
        "subject": "Weekly Sales Report",
        "body": email_body
    }
}

# Create approval request
approval_id = approval_manager.create_approval_request(task, action_details)

# After approval, execute
if status == ApprovalStatus.APPROVED:
    result = mcp_client.execute(
        server=action_details["mcp_server"],
        method=action_details["method"],
        parameters=action_details["parameters"]
    )
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` | Yes |
| `EMAIL_PORT` | SMTP server port | `587` | Yes |
| `EMAIL_SECURE` | Use SSL (true for 465) | `false` | No |
| `EMAIL_USER` | SMTP username | - | Yes |
| `EMAIL_PASSWORD` | SMTP password | - | Yes |
| `EMAIL_FROM` | Default sender | `EMAIL_USER` | No |
| `LOG_LEVEL` | Logging level | `info` | No |
| `MAX_EMAIL_SIZE` | Max email size (bytes) | `10485760` | No |
| `MAX_RECIPIENTS` | Max recipients per email | `50` | No |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | `60` | No |

### Security Configuration

**Domain Filtering:**
```env
# Only allow these domains
ALLOWED_DOMAINS=company.com,partner.com

# Block these domains
BLOCKED_DOMAINS=spam.com,blocked.com
```

**Rate Limiting:**
```env
# Maximum emails per minute
RATE_LIMIT_PER_MINUTE=60
```

**Size Limits:**
```env
# Maximum email size (10MB)
MAX_EMAIL_SIZE=10485760

# Maximum recipients (to + cc + bcc)
MAX_RECIPIENTS=50
```

## Logging

Logs are written to `logs/` directory:

- `email-server.log` - All logs
- `email-server-error.log` - Errors only
- `exceptions.log` - Uncaught exceptions
- `rejections.log` - Unhandled promise rejections

**View logs:**
```bash
# Tail all logs
tail -f logs/email-server.log

# Tail errors only
tail -f logs/email-server-error.log

# Search logs
grep "email-" logs/email-server.log
```

**Log format:**
```json
{
  "timestamp": "2026-02-13 15:30:45",
  "level": "info",
  "message": "Email sent successfully",
  "service": "email-mcp-server",
  "requestId": "email-1234567890-abc123",
  "messageId": "<unique-id@gmail.com>",
  "to": "recipient@example.com",
  "duration": "1234ms"
}
```

## Error Handling

The server handles errors gracefully and returns structured error responses:

**Validation Error:**
```json
{
  "success": false,
  "error": "Validation failed",
  "validationErrors": [
    {
      "field": "to",
      "message": "Invalid recipient email address"
    }
  ]
}
```

**Rate Limit Error:**
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "retryAfter": 30,
  "resetAt": "2026-02-13T15:31:00.000Z"
}
```

**SMTP Error:**
```json
{
  "success": false,
  "error": "Connection timeout",
  "errorCode": "ETIMEDOUT",
  "duration": 10000
}
```

## Testing

Run the test suite:

```bash
npm test
```

**Test coverage:**
- ✅ Email validation (8 tests)
- ✅ Rate limiting (4 tests)
- ✅ Email service initialization (2 tests)
- ✅ Integration workflow (1 test)

## Troubleshooting

### Issue: "Missing credentials" error

**Solution:**
1. Check `.env` file exists
2. Verify `EMAIL_USER` and `EMAIL_PASSWORD` are set
3. For Gmail, use App Password (not regular password)

### Issue: "Connection timeout"

**Solution:**
1. Check SMTP host and port are correct
2. Verify firewall allows outbound connections on port 587/465
3. Test connection: `npm test`

### Issue: "Authentication failed"

**Solution:**
1. For Gmail: Enable 2FA and generate App Password
2. For other providers: Verify credentials are correct
3. Check if account requires "less secure app access"

### Issue: Rate limit exceeded

**Solution:**
1. Wait for rate limit to reset (shown in error response)
2. Increase `RATE_LIMIT_PER_MINUTE` in `.env`
3. Implement request queuing in your application

## Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use App Passwords** - Don't use your main account password
3. **Enable domain filtering** - Restrict allowed recipient domains
4. **Monitor logs** - Watch for suspicious activity
5. **Rotate credentials** - Change passwords regularly
6. **Use TLS** - Always use port 587 with TLS (not port 25)
7. **Validate input** - Server validates all input, but validate on client too
8. **Rate limiting** - Prevents abuse and protects your SMTP quota

## Performance

- **Throughput**: 60 emails/minute (configurable)
- **Latency**: 1-3 seconds per email (depends on SMTP server)
- **Memory**: ~50MB base + ~1MB per concurrent request
- **CPU**: Minimal (<5% on modern hardware)

## Production Deployment

### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/email-mcp-server.service`:

```ini
[Unit]
Description=MCP Email Server
After=network.target

[Service]
Type=simple
User=fte
WorkingDirectory=/path/to/silver-tier/mcp/email-server
ExecStart=/usr/bin/node src/server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable email-mcp-server
sudo systemctl start email-mcp-server
sudo systemctl status email-mcp-server
```

### Option 2: Docker

Create `Dockerfile`:

```dockerfile
FROM node:24-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY src ./src
COPY .env .env

EXPOSE 3000

CMD ["node", "src/server.js"]
```

Build and run:
```bash
docker build -t email-mcp-server .
docker run -d --name email-server email-mcp-server
```

### Option 3: PM2 Process Manager

```bash
npm install -g pm2

# Start server
pm2 start src/server.js --name email-server

# Monitor
pm2 monit

# Logs
pm2 logs email-server

# Restart
pm2 restart email-server
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check logs: `logs/email-server.log`
- Run tests: `npm test`
- Review documentation: This README
- Check configuration: `.env` file

## Changelog

### v1.0.0 (2026-02-13)
- Initial release
- MCP protocol integration
- Email sending with nodemailer
- Validation with Joi
- Rate limiting
- Comprehensive logging
- Security features
- Production-ready architecture
