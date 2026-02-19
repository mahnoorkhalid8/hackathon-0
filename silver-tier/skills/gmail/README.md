# Gmail Skills

Reusable skills for Gmail automation and email management.

## Available Skills

### 1. send-email
Send emails with optional attachments and HTML formatting.

**Command:**
```bash
python scripts/send_email.py
```

**Features:**
- Send to single or multiple recipients
- Add CC and BCC
- Attach files
- HTML or plain text
- Template support

### 2. read-emails
Read and filter emails from inbox.

**Command:**
```bash
python scripts/read_emails.py
```

**Features:**
- Read unread emails
- Filter by sender, subject, date
- Mark as read/unread
- Export to JSON/CSV

### 3. search-emails
Search emails by various criteria.

**Command:**
```bash
python scripts/search_emails.py
```

**Features:**
- Search by keyword
- Filter by date range
- Search in specific labels
- Advanced query support

### 4. manage-labels
Organize emails with labels.

**Command:**
```bash
python scripts/manage_labels.py
```

**Features:**
- Create/delete labels
- Apply labels to emails
- List all labels
- Bulk label operations

## Setup

### Prerequisites

1. **Gmail API Credentials:**
   - Go to Google Cloud Console
   - Enable Gmail API
   - Download credentials.json
   - Place in `gmail/` folder

2. **Python Dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### First Time Authentication

Run any script for the first time:
```bash
python scripts/send_email.py
```

This will:
1. Open browser for Google authentication
2. Save token.json for future use
3. No re-authentication needed after this

## Usage Examples

### Send Simple Email
```bash
cd skills/gmail
python scripts/send_email.py
# Follow prompts to enter recipient, subject, message
```

### Read Unread Emails
```bash
python scripts/read_emails.py --unread --limit 10
```

### Search Emails
```bash
python scripts/search_emails.py --query "from:example@gmail.com" --after "2024/01/01"
```

## Configuration

Edit `config.json` to set defaults:
```json
{
  "default_sender": "your-email@gmail.com",
  "signature": "Sent via Gmail Skills",
  "max_results": 50
}
```

## Skill Definitions

All skill command definitions are in the `commands/` folder:
- `send-email.skill` - Email sending interface
- `read-emails.skill` - Email reading interface
- `search-emails.skill` - Email search interface
- `manage-labels.skill` - Label management interface

## Implementation

All implementation scripts are in the `scripts/` folder and reference the main Gmail implementation in `../../gmail/`.

## Troubleshooting

**Issue: "credentials.json not found"**
- Download from Google Cloud Console
- Place in `../../gmail/` folder

**Issue: "Token expired"**
- Delete token.json
- Run script again to re-authenticate

**Issue: "Permission denied"**
- Check Gmail API is enabled
- Verify OAuth scopes in credentials

## Related Documentation

- Main Gmail implementation: `../../gmail/README.md`
- Gmail API docs: https://developers.google.com/gmail/api
