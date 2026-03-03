# Gmail API Setup Guide

## Overview

This system uses **Gmail API with OAuth2** to send emails. Since you've already authenticated with Google Cloud, you just need to ensure your credentials are properly configured.

## Prerequisites

✅ Google Cloud account (you already have this)
✅ Gmail API enabled in Google Cloud Console
✅ OAuth2 credentials downloaded

## Required Files

You need two files in your project root:

1. **credentials.json** - OAuth2 client credentials from Google Cloud Console
2. **token.json** - Refresh token (generated automatically on first run)

---

## Step 1: Get credentials.json

If you don't already have `credentials.json`:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Choose **Desktop app** as application type
6. Download the JSON file
7. Rename it to `credentials.json`
8. Place it in the project root: `C:\Users\SEVEN86 COMPUTES\hackthon-0\silver-tier\credentials.json`

### Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

---

## Step 2: Generate token.json (First Time Only)

The first time you run the email system, it will generate `token.json`:

```bash
# Install dependencies
pip install -r requirements.txt

# Run CEO report (this will trigger authentication)
python run_agent.py ceo-report
```

**What happens:**
1. A browser window will open
2. Sign in with your Gmail account (khalidmahnoor889@gmail.com)
3. Grant permissions to send emails
4. `token.json` will be created automatically
5. Future runs will use this token (no browser needed)

---

## Step 3: Verify Configuration

Check that your `.env` file has:

```bash
CEO_EMAIL=khalidmahnoor889@gmail.com
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
```

---

## File Structure

```
silver-tier/
├── credentials.json          # OAuth2 credentials (from Google Cloud)
├── token.json               # Refresh token (auto-generated)
├── .env                     # Configuration
├── gmail_api_service.py     # Gmail API service
├── run_agent.py             # Main script
└── send_custom_email.py     # Custom email sender
```

---

## Testing

### Test CEO Briefing Email

```bash
python run_agent.py ceo-report
```

This will:
- Analyze tasks from vault directories
- Generate CEO briefing
- Send email to khalidmahnoor889@gmail.com

### Test Custom Email

```bash
python send_custom_email.py
```

Then provide:
- Recipient email
- Subject
- Content

---

## Troubleshooting

### Error: "credentials.json not found"

**Solution:** Download credentials.json from Google Cloud Console and place it in project root.

### Error: "token.json not found"

**Solution:** Run the script once. It will open a browser for authentication and create token.json.

### Error: "Token expired"

**Solution:** Delete token.json and run again. It will re-authenticate.

```bash
rm token.json
python run_agent.py ceo-report
```

### Error: "Gmail API not enabled"

**Solution:** Enable Gmail API in Google Cloud Console:
1. Go to APIs & Services > Library
2. Search "Gmail API"
3. Click Enable

### Error: "Access denied"

**Solution:** Make sure you granted "Send email" permission during OAuth consent.

---

## Security Notes

🔒 **credentials.json** - Contains OAuth2 client ID and secret (keep private)
🔒 **token.json** - Contains refresh token (keep private)
🔒 **Never commit these files to Git** (already in .gitignore)

---

## Advantages of Gmail API vs SMTP

✅ **More secure** - OAuth2 instead of passwords
✅ **Higher limits** - 2,000 emails/day (vs 500 for SMTP)
✅ **Better error handling** - Detailed API responses
✅ **No app passwords needed** - Uses OAuth2 tokens
✅ **Official Google API** - Better support and reliability

---

## What You Already Have

Since you authenticated with Google Cloud, you likely have:
- ✅ Google Cloud project
- ✅ Gmail API enabled
- ✅ OAuth2 credentials

You just need to:
1. Download credentials.json (if not already done)
2. Run the script once to generate token.json
3. Start sending emails!

---

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run CEO report (will authenticate on first run)
python run_agent.py ceo-report

# 3. Send custom email
python send_custom_email.py
```

---

## Next Steps

1. Place `credentials.json` in project root
2. Run `python run_agent.py ceo-report`
3. Authenticate in browser (one time only)
4. Email will be sent to khalidmahnoor889@gmail.com
5. Set up scheduler for automatic Monday 9 AM emails

---

**Need Help?**

If you encounter issues:
1. Check that credentials.json exists
2. Check that Gmail API is enabled
3. Check logs: `logs/run_agent_*.log`
4. Try deleting token.json and re-authenticating
