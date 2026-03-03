# WhatsApp Skills

Reusable skills for WhatsApp automation and messaging.

## Available Skills

### 1. send-message
Send WhatsApp messages by selecting contacts by name.

**Command:**
```bash
python scripts/send_message.py
```

**Features:**
- Browse contacts by name
- Search contacts
- Pagination support
- Message confirmation
- No phone number needed

### 2. auto-respond
AI-powered automatic message responder.

**Command:**
```bash
python scripts/auto_respond.py
```

**Features:**
- Monitor incoming messages
- Generate AI responses (Claude API)
- Fallback responses without API
- Human-in-the-loop approval
- Message logging

### 3. view-contacts
List and search WhatsApp contacts.

**Command:**
```bash
python scripts/view_contacts.py
```

**Features:**
- List recent contacts
- Search by name
- Export to JSON/CSV
- Show contact details

### 4. check-status
Check WhatsApp connection and session status.

**Command:**
```bash
python scripts/check_status.py
```

**Features:**
- Connection status
- Account information
- Session validity
- Message statistics

## Setup

### Prerequisites

1. **Node.js Backend (Required):**
```bash
cd ../../whatsapp-node
npm install
npm start
```

2. **Python Dependencies:**
```bash
pip install requests anthropic
```

3. **First Time Authentication:**
   - Start Node.js backend: `npm start`
   - Scan QR code with WhatsApp mobile app
   - Session saved to `.wwebjs_auth/` folder
   - No QR scan needed after this

### Optional: Claude API Key

For intelligent AI responses (optional):
```bash
# Edit ../../whatsapp-node/.env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Without API key: Uses simple fallback responses

## Usage Examples

### Send Message
```bash
cd skills/whatsapp
python scripts/send_message.py
# Browse contacts, select, type message, send
```

### Start Auto-Responder
```bash
python scripts/auto_respond.py
# Monitors and responds to incoming messages automatically
```

### View Contacts
```bash
python scripts/view_contacts.py --search "john" --limit 20
```

### Check Status
```bash
python scripts/check_status.py
# Shows connection status, account info, statistics
```

## Configuration

Edit `../../whatsapp-node/whatsapp_state.json`:
```json
{
  "human_in_the_loop": false,
  "watcher_config": {
    "poll_interval_seconds": 5,
    "auto_reply_enabled": true,
    "process_group_messages": false
  }
}
```

**Options:**
- `human_in_the_loop`: Require approval before sending replies
- `auto_reply_enabled`: Enable/disable auto-responses
- `poll_interval_seconds`: How often to check for messages
- `process_group_messages`: Respond in group chats

## Skill Definitions

All skill command definitions are in the `commands/` folder:
- `send-message.skill` - Message sending interface
- `auto-respond.skill` - Auto-responder interface
- `view-contacts.skill` - Contact viewing interface
- `check-status.skill` - Status checking interface

## Implementation

All implementation scripts are in the `scripts/` folder and reference the main WhatsApp implementation in `../../whatsapp-node/`.

## Architecture

```
┌─────────────────────────────────────────┐
│  Skills Layer (This folder)             │
│  - Simple command interface             │
│  - User-friendly scripts                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  WhatsApp Node Backend                  │
│  - Express API (port 3000)              │
│  - WhatsApp Web client                  │
│  - Session management                   │
└─────────────────────────────────────────┘
```

## Troubleshooting

**Issue: "Cannot connect to WhatsApp backend"**
- Make sure Node.js server is running: `npm start`
- Check server is on port 3000
- Verify WhatsApp is authenticated

**Issue: "Session invalid"**
- Restart Node.js server
- Scan QR code again if prompted
- Check `.wwebjs_auth/` folder exists

**Issue: "No contacts found"**
- Make sure you have recent WhatsApp conversations
- Restart Node.js server
- Try sending a message to someone first

**Issue: "Message failed to send"**
- Check phone number format (country code, no +)
- Verify recipient has WhatsApp
- Check internet connection

## Related Documentation

- Main WhatsApp implementation: `../../whatsapp-node/README.md`
- Setup guide: `../../whatsapp-node/SETUP_GUIDE.md`
- State management: `../../whatsapp-node/STATE_MANAGEMENT_GUIDE.md`
- Claude integration: `../../whatsapp-node/CLAUDE_ASSISTANT_GUIDE.md`

## Notes

- **No QR scan needed** after initial setup (session persists)
- **Contact names** used instead of phone numbers
- **AI responses** optional (works without API key)
- **Human approval** configurable for safety
- **Message logging** automatic in whatsapp_state.json
