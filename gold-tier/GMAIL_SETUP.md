# Gmail Watcher Setup Instructions

## Complete Setup Guide for Gmail Watcher Service

This guide will walk you through setting up the Gmail watcher service from scratch.

---

## Prerequisites

- Python 3.13+
- Google account with Gmail
- Google Cloud Console access
- Silver Tier Digital FTE installed

---

## Step 1: Install Required Libraries

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or use the requirements file:

```bash
pip install -r requirements_gmail.txt
```

---

## Step 2: Set Up Google Cloud Project

### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Silver Tier FTE Gmail"
4. Click "Create"

### 2.2 Enable Gmail API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

### 2.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (or Internal if using Google Workspace)
   - App name: "Silver Tier FTE Gmail Watcher"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip for now (click "Save and Continue")
   - Test users: Add your email
   - Click "Save and Continue"
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Gmail Watcher Desktop"
   - Click "Create"
5. Click "Download JSON"
6. Save the file as `config/gmail_credentials.json`

---

## Step 3: Configure the Service

### 3.1 Create Configuration Directory

```bash
mkdir -p config
```

### 3.2 Place Credentials File

Move the downloaded JSON file:

```bash
mv ~/Downloads/client_secret_*.json config/gmail_credentials.json
```

### 3.3 Create Configuration File (Optional)

Create `config/gmail_watcher_config.yaml`:

```yaml
inbox_path: "vault/Inbox"
credentials_file: "config/gmail_credentials.json"
token_file: "config/gmail_token.pickle"
check_interval: 120  # 2 minutes
max_results: 10
mark_as_read: false
log_level: "INFO"
```

---

## Step 4: First Run - Authentication

### 4.1 Run the Service

```bash
python gmail_watcher_service.py
```

### 4.2 Complete OAuth Flow

1. A browser window will open automatically
2. Sign in to your Google account
3. Review the permissions requested
4. Click "Allow"
5. You should see "The authentication flow has completed"
6. Close the browser window

### 4.3 Verify Token Created

Check that the token file was created:

```bash
ls -la config/gmail_token.pickle
```

---

## Step 5: Test the Service

### 5.1 Send a Test Email

Send an email to your Gmail account with:
- Subject: "Test Email for FTE"
- Body: "This is a test email to verify the Gmail watcher is working."

### 5.2 Watch the Service

The service will:
1. Check for unread emails every 2 minutes
2. Find your test email
3. Save it to `vault/Inbox/email-*.md`
4. Log the activity

### 5.3 Verify Email Saved

```bash
ls -la vault/Inbox/email-*.md
cat vault/Inbox/email-*.md
```

---

## Step 6: Integration with File Watcher

The Gmail watcher saves emails to `vault/Inbox/`, which is monitored by the file watcher service.

### 6.1 Start File Watcher (if not running)

```bash
# Terminal 1: Gmail Watcher
python gmail_watcher_service.py

# Terminal 2: File Watcher
python file_watcher_service.py
```

### 6.2 Complete Flow

```
New Email → Gmail Watcher → vault/Inbox/email.md → File Watcher → Agent Loop
```

---

## Configuration Options

### Basic Configuration

```python
from gmail_watcher_service import GmailWatcherConfig

config = GmailWatcherConfig(
    inbox_path="vault/Inbox",
    check_interval=120,  # 2 minutes
    max_results=10,
    mark_as_read=False,
    log_level="INFO"
)
```

### Advanced Configuration

```python
config = GmailWatcherConfig(
    inbox_path="vault/Inbox",
    credentials_file="config/gmail_credentials.json",
    token_file="config/gmail_token.pickle",
    check_interval=60,  # 1 minute (more frequent)
    max_results=20,  # More emails per check
    mark_as_read=True,  # Auto-mark as read
    log_level="DEBUG"  # More verbose logging
)
```

---

## Troubleshooting

### Issue: "Credentials file not found"

**Solution:**
```bash
# Verify file exists
ls -la config/gmail_credentials.json

# If not, download from Google Cloud Console
# Place in config/ directory
```

### Issue: "Authentication failed"

**Solution:**
1. Delete existing token: `rm config/gmail_token.pickle`
2. Run service again: `python gmail_watcher_service.py`
3. Complete OAuth flow again

### Issue: "Access blocked: This app's request is invalid"

**Solution:**
1. Go to Google Cloud Console
2. OAuth consent screen
3. Add your email to "Test users"
4. Try authentication again

### Issue: "No unread emails found" (but you have unread emails)

**Solution:**
1. Check Gmail API is enabled in Cloud Console
2. Verify OAuth scopes include `gmail.readonly`
3. Check logs: `tail -f logs/gmail_watcher.log`

### Issue: "Quota exceeded"

**Solution:**
1. Gmail API has daily quotas
2. Default: 1 billion quota units/day
3. Each read operation: ~5 units
4. Increase check_interval if hitting limits

---

## Security Best Practices

### 1. Protect Credentials

```bash
# Set proper permissions
chmod 600 config/gmail_credentials.json
chmod 600 config/gmail_token.pickle

# Add to .gitignore
echo "config/gmail_credentials.json" >> .gitignore
echo "config/gmail_token.pickle" >> .gitignore
```

### 2. Use Service Account (Production)

For production deployments, consider using a service account instead of OAuth:

1. Create service account in Google Cloud Console
2. Enable domain-wide delegation
3. Use service account credentials

### 3. Limit Scopes

Only request necessary scopes:
- `gmail.readonly` - Read-only access (recommended)
- `gmail.modify` - If you need to mark as read
- Avoid `gmail.full` unless absolutely necessary

---

## Running as a Service

### Systemd (Linux)

Create `/etc/systemd/system/gmail-watcher.service`:

```ini
[Unit]
Description=Gmail Watcher Service
After=network.target

[Service]
Type=simple
User=fte
WorkingDirectory=/opt/silver-tier-fte
ExecStart=/usr/bin/python3 gmail_watcher_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable gmail-watcher
sudo systemctl start gmail-watcher
sudo systemctl status gmail-watcher
```

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements_gmail.txt .
RUN pip install -r requirements_gmail.txt

COPY . .

# Mount config directory with credentials
VOLUME /app/config

CMD ["python", "gmail_watcher_service.py"]
```

Run:

```bash
docker build -t gmail-watcher .
docker run -v $(pwd)/config:/app/config gmail-watcher
```

---

## Monitoring

### Check Logs

```bash
# Real-time monitoring
tail -f logs/gmail_watcher.log

# Search for errors
grep ERROR logs/gmail_watcher.log

# Check statistics
grep "Service Statistics" logs/gmail_watcher.log
```

### Service Status

```python
from gmail_watcher_service import GmailWatcherService

service = GmailWatcherService()
status = service.get_status()

print(f"Running: {status['running']}")
print(f"Emails processed: {status['emails_processed']}")
```

---

## Performance

### Typical Performance

- **Check latency:** 1-3 seconds per check
- **Email processing:** 0.5-1 second per email
- **Memory usage:** 50-100MB
- **API quota usage:** ~50 units per check

### Optimization Tips

1. **Adjust check interval** based on email volume
2. **Limit max_results** to reduce API calls
3. **Use mark_as_read** to avoid reprocessing
4. **Monitor quota usage** in Google Cloud Console

---

## FAQ

**Q: Can I monitor multiple Gmail accounts?**
A: Yes, create separate instances with different credentials and token files.

**Q: Will this work with Google Workspace accounts?**
A: Yes, follow the same setup process. May need admin approval for OAuth consent.

**Q: Can I filter which emails to process?**
A: Yes, modify the query in `get_unread_emails()`. Examples:
- `q='is:unread from:specific@email.com'`
- `q='is:unread subject:important'`
- `q='is:unread label:work'`

**Q: What happens if the service crashes?**
A: Unread emails remain unread and will be processed on next run. No emails are lost.

**Q: Can I process emails in real-time?**
A: Gmail API doesn't support push notifications for personal accounts. Use Gmail Pub/Sub for real-time (requires Google Workspace).

---

## Next Steps

1. **Test thoroughly** with various email types
2. **Adjust configuration** based on your needs
3. **Set up monitoring** and alerts
4. **Integrate with agent loop** for automated processing
5. **Consider backup** of processed emails

---

## Support

**Logs:** `logs/gmail_watcher.log`
**Documentation:** This file
**Google Cloud Console:** https://console.cloud.google.com/
**Gmail API Docs:** https://developers.google.com/gmail/api

---

**Version:** 1.0.0
**Status:** Production Ready
**Last Updated:** 2026-02-13
