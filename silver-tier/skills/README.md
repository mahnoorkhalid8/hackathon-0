# Skills Directory

This directory contains reusable skills for Gmail and WhatsApp automation implemented in the Silver Tier.

## Structure

```
skills/
├── gmail/
│   ├── commands/       # Skill command definitions
│   ├── scripts/        # Implementation scripts
│   └── README.md       # Gmail skills documentation
├── whatsapp/
│   ├── commands/       # Skill command definitions
│   ├── scripts/        # Implementation scripts
│   └── README.md       # WhatsApp skills documentation
└── README.md          # This file
```

## Available Skills

### Gmail Skills
- **send-email** - Send emails with attachments
- **read-emails** - Read and filter emails
- **search-emails** - Search emails by criteria
- **manage-labels** - Organize emails with labels

### WhatsApp Skills
- **send-message** - Send messages by contact name
- **auto-respond** - AI-powered auto-responder
- **view-contacts** - List and search contacts
- **check-status** - Check WhatsApp connection status

## Usage

Each skill has:
1. **Command file** - Defines the skill interface and parameters
2. **Script file** - Contains the implementation
3. **Documentation** - Usage examples and requirements

## Quick Start

### Gmail
```bash
cd gmail
python scripts/send_email.py
```

### WhatsApp
```bash
cd whatsapp
python scripts/send_message.py
```

## Requirements

- Python 3.8+
- Node.js 16+ (for WhatsApp)
- Gmail API credentials (for Gmail)
- Authenticated WhatsApp session (for WhatsApp)

See individual skill READMEs for detailed setup instructions.
