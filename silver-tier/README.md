# Silver Tier - Gmail, WhatsApp & LinkedIn Automation

**Version:** 1.0
**Status:** Production Ready
**Created:** 2026-02-17
**Python:** 3.8+
**Node.js:** 16+

---

## Overview

Silver Tier provides production-ready automation for Gmail, WhatsApp, and LinkedIn with complete tools for communication and lead generation.

**What You Get:**
- ✓ Gmail automation (send, read, search, manage labels)
- ✓ WhatsApp messaging (send by contact name, auto-respond, view contacts)
- ✓ LinkedIn content strategy & lead generation
- ✓ AI-powered auto-responder with Claude API
- ✓ Contact name-based messaging (no phone numbers needed)
- ✓ Session persistence (no QR scan after first time)
- ✓ Organized skills folder with reusable commands
- ✓ Complete documentation and examples

---

## Quick Start

### Gmail Skills

**Prerequisites:**
```bash
# Install Python dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Get Gmail API credentials from Google Cloud Console
# Place credentials.json in gmail/ folder
```

**Send an email:**
```bash
cd skills/gmail
python scripts/send_email.py
```

### WhatsApp Skills

**Prerequisites:**
```bash
# Install Node.js dependencies
cd whatsapp-node
npm install

# Install Python dependencies
pip install requests anthropic

# Start Node.js backend
npm start
# Scan QR code with WhatsApp mobile app (first time only)
```

**Send a message:**
```bash
cd skills/whatsapp
python scripts/send_message.py
```

### LinkedIn Automation

**Prerequisites:**
```bash
# No external dependencies required
# All tools use Python standard library
```

**Generate content strategy:**
```bash
cd linkedin
python linkedin_strategy_generator.py --interactive
```

**Generate posts:**
```bash
python linkedin_post_generator.py --pillar all
```

**Create content calendar:**
```bash
python linkedin_calendar_generator.py --weeks 4
```

---

## Project Structure

```
silver-tier/
│
├── 📧 gmail/                      # Gmail implementation
│   ├── credentials.json          # Gmail API credentials
│   ├── token.json               # Saved authentication
│   └── *.py                     # Gmail scripts
│
├── 💬 whatsapp-node/             # WhatsApp implementation
│   ├── server.js                # Express backend
│   ├── src/                     # WhatsApp service
│   ├── send_message.py          # Message sender
│   ├── whatsapp_watcher.py      # Auto-responder
│   ├── whatsapp_assistant.py    # AI assistant
│   ├── state_manager.py         # State management
│   └── whatsapp_state.json      # Session & logs
│
├── 💼 linkedin/                  # LinkedIn automation (NEW)
│   ├── README.md                # LinkedIn documentation
│   ├── linkedin_strategy_generator.py    # Strategy generator
│   ├── linkedin_post_generator.py        # Post generator
│   ├── linkedin_calendar_generator.py    # Calendar generator
│   ├── linkedin_lead_tracker.py          # Lead tracking
│   ├── Plan.md                  # Generated strategy (output)
│   ├── content_calendar.json    # Generated calendar (output)
│   ├── generated_posts.json     # Generated posts (output)
│   └── leads.json              # Lead tracking data (output)
│
└── 🛠️ skills/                    # Skills interface
    ├── README.md                # Skills documentation
    ├── SKILLS_SUMMARY.md        # Complete summary
    │
    ├── gmail/                   # Gmail skills
    │   ├── README.md
    │   ├── commands/            # 4 skill definitions
    │   │   ├── send-email.skill
    │   │   ├── read-emails.skill
    │   │   ├── search-emails.skill
    │   │   └── manage-labels.skill
    │   └── scripts/             # 4 implementation scripts
    │       ├── send_email.py
    │       ├── read_emails.py
    │       ├── search_emails.py
    │       └── manage_labels.py
    │
    └── whatsapp/                # WhatsApp skills
        ├── README.md
        ├── commands/            # 4 skill definitions
        │   ├── send-message.skill
        │   ├── auto-respond.skill
        │   ├── view-contacts.skill
        │   └── check-status.skill
        └── scripts/             # 4 implementation scripts
            ├── send_message.py
            ├── auto_respond.py
            ├── view_contacts.py
            └── check_status.py
```

---

## Skills System

### What are Skills?

Skills are reusable, documented automation commands for common Gmail and WhatsApp operations. Each skill has:

1. **Skill Definition** (`.skill` file) - Interface specification, parameters, examples
2. **Implementation Script** (`.py` file) - Working code with CLI interface
3. **Documentation** (README) - Setup guide, usage examples, troubleshooting

### Available Skills

#### Gmail Skills (4)

| Skill | Description | Command |
|-------|-------------|---------|
| **send-email** | Send emails with attachments | `python scripts/send_email.py` |
| **read-emails** | Read and filter emails | `python scripts/read_emails.py --unread` |
| **search-emails** | Search by criteria | `python scripts/search_emails.py --keyword "invoice"` |
| **manage-labels** | Organize with labels | `python scripts/manage_labels.py --action list` |

#### WhatsApp Skills (4)

| Skill | Description | Command |
|-------|-------------|---------|
| **send-message** | Send by contact name | `python scripts/send_message.py` |
| **auto-respond** | AI-powered auto-responder | `python scripts/auto_respond.py` |
| **view-contacts** | List and search contacts | `python scripts/view_contacts.py --search "john"` |
| **check-status** | Connection status | `python scripts/check_status.py --detailed` |

---

## Gmail Setup

### 1. Get API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Place in `gmail/` folder

### 2. First Time Authentication

```bash
cd skills/gmail
python scripts/send_email.py
```

This will:
- Open browser for Google authentication
- Save `token.json` for future use
- No re-authentication needed after this

### 3. Usage Examples

**Send email:**
```bash
python scripts/send_email.py \
  --to "user@example.com" \
  --subject "Test" \
  --body "Hello!"
```

**Read unread emails:**
```bash
python scripts/read_emails.py --unread --limit 10
```

**Search emails:**
```bash
python scripts/search_emails.py \
  --keyword "invoice" \
  --after "2024-01-01" \
  --has-attachment
```

**List labels:**
```bash
python scripts/manage_labels.py --action list
```

---

## WhatsApp Setup

### 1. Start Node.js Backend

```bash
cd whatsapp-node
npm install
npm start
```

**First time:** Scan QR code with WhatsApp mobile app
**Subsequent runs:** No QR scan needed (session saved)

### 2. Usage Examples

**Send message (interactive):**
```bash
cd skills/whatsapp
python scripts/send_message.py
# Browse contacts by name, select, type message, send
```

**Check status:**
```bash
python scripts/check_status.py --detailed
```

**View contacts:**
```bash
python scripts/view_contacts.py --search "john"
```

**Start auto-responder:**
```bash
python scripts/auto_respond.py
# Monitors incoming messages and responds automatically
```

---

## WhatsApp Auto-Responder

### Features

- **AI-Powered**: Uses Claude API for intelligent responses
- **Fallback Mode**: Works without API key (simple responses)
- **Human-in-the-Loop**: Optional approval before sending
- **Message Logging**: All activity logged to whatsapp_state.json
- **Session Persistence**: No QR scan after first time

### Setup Claude API (Optional)

For intelligent AI responses:

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Edit `whatsapp-node/.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
3. Restart Node.js backend

**Without API key:** Uses simple keyword-based responses
**With API key:** Full Claude AI intelligence

### Configuration

Edit `whatsapp-node/whatsapp_state.json`:

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

---

## Complete Workflows

### Workflow 1: Send Email with Attachment

```bash
cd skills/gmail
python scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Documents" \
  --body "Please find attached" \
  --attachments "file.pdf" "file2.docx"
```

### Workflow 2: WhatsApp Auto-Responder

**Terminal 1 - Backend:**
```bash
cd whatsapp-node
npm start
```

**Terminal 2 - Auto-Responder:**
```bash
cd skills/whatsapp
python scripts/auto_respond.py --human-approval
```

Now incoming WhatsApp messages will:
1. Be detected automatically
2. Generate AI response
3. Ask for your approval
4. Send reply

### Workflow 3: LinkedIn Lead Generation Campaign

**Step 1: Generate Strategy**
```bash
cd linkedin
python linkedin_strategy_generator.py \
  --business "AI automation consulting" \
  --target "small businesses" \
  --goal "generate 10 leads per month"
```

**Step 2: Create Content Calendar**
```bash
python linkedin_calendar_generator.py --weeks 4
```

**Step 3: Generate Posts**
```bash
python linkedin_post_generator.py --pillar all --count 3
```

**Step 4: Track Leads**
```bash
python linkedin_lead_tracker.py --action add
python linkedin_lead_tracker.py --action stats
```

### Workflow 4: Search and Export Contacts

```bash
cd skills/whatsapp
python scripts/view_contacts.py \
  --search "work" \
  --export json \
  --output work_contacts.json
```

---

## LinkedIn Automation

### Overview

Complete LinkedIn toolkit for content strategy, post generation, and lead tracking. Designed to generate consistent leads through strategic LinkedIn presence.

**Tools Available:**
- **Strategy Generator:** Create comprehensive content strategy
- **Post Generator:** Generate posts for all content pillars
- **Calendar Generator:** Create weekly/monthly content calendars
- **Lead Tracker:** Track and manage LinkedIn leads

### Quick Start

**Generate Strategy:**
```bash
cd linkedin
python linkedin_strategy_generator.py --interactive
```

**Generate Posts:**
```bash
python linkedin_post_generator.py --pillar all
```

**Create Calendar:**
```bash
python linkedin_calendar_generator.py --weeks 4
```

**Track Leads:**
```bash
python linkedin_lead_tracker.py --action add
```

### Content Strategy

LinkedIn automation follows a proven 4-pillar content strategy:
- **Educational (40%):** How-to guides, frameworks, industry insights
- **Social Proof (30%):** Case studies, testimonials, results
- **Engagement (20%):** Questions, polls, discussions
- **Promotional (10%):** Offers, resources, consultations

**Weekly Schedule:**
- Monday 9 AM: Educational (Carousel/Article)
- Tuesday 12 PM: Engagement (Question/Poll)
- Wednesday 10 AM: Social Proof (Case Study)
- Thursday 2 PM: Educational (Video/Infographic)
- Friday 11 AM: Engagement (Behind-the-scenes)

**Lead Generation Timeline:**
- Month 1: Foundation (2-3 leads)
- Month 2: Growth (5-7 leads)
- Month 3: Momentum (10+ leads)
- Month 4+: Scale (consistent lead flow)

For complete LinkedIn documentation, see `linkedin/README.md`.

---

## Documentation

### Main Documentation

| Document | Purpose |
|----------|---------|
| **skills/README.md** | Skills system overview |
| **skills/SKILLS_SUMMARY.md** | Complete summary |
| **skills/gmail/README.md** | Gmail skills guide |
| **skills/whatsapp/README.md** | WhatsApp skills guide |
| **linkedin/README.md** | LinkedIn automation guide |

### Implementation Documentation

| Document | Purpose |
|----------|---------|
| **whatsapp-node/README.md** | WhatsApp API reference |
| **whatsapp-node/SETUP_GUIDE.md** | Complete setup walkthrough |
| **whatsapp-node/STATE_MANAGEMENT_GUIDE.md** | State management details |
| **whatsapp-node/CLAUDE_ASSISTANT_GUIDE.md** | Claude API integration |

### LinkedIn Documentation

| Document | Purpose |
|----------|---------|
| **linkedin/README.md** | Complete LinkedIn automation guide |
| **linkedin/Plan.md** | Generated content strategy (output) |
| **linkedin/content_calendar.md** | Generated calendar (output) |
| **linkedin/generated_posts.json** | Generated posts (output) |

### Skill Definitions

Each skill has a `.skill` file in `commands/` folder with:
- Interface specification
- Parameters and options
- Usage examples
- Return values
- Requirements

---

## Troubleshooting

### Gmail Issues

**"credentials.json not found"**
- Download from Google Cloud Console
- Place in `gmail/` folder

**"Token expired"**
- Delete `token.json`
- Run script again to re-authenticate

**"Permission denied"**
- Check Gmail API is enabled
- Verify OAuth scopes in credentials

### WhatsApp Issues

**"Cannot connect to WhatsApp backend"**
- Make sure Node.js server is running: `npm start`
- Check server is on port 3000
- Verify WhatsApp is authenticated

**"Session invalid"**
- Restart Node.js server
- Scan QR code again if prompted
- Check `.wwebjs_auth/` folder exists

**"No contacts found"**
- Make sure you have recent WhatsApp conversations
- Restart Node.js server
- Try sending a message to someone first

**"Message failed to send"**
- Check phone number format (country code, no +)
- Verify recipient has WhatsApp
- Check internet connection

---

## Performance

### Gmail
- **Authentication:** One-time (token cached)
- **Send Email:** 1-3 seconds
- **Read Emails:** 2-5 seconds
- **Search:** 3-10 seconds (depends on query)

### WhatsApp
- **Backend Startup:** 10-30 seconds (first time with QR)
- **Backend Startup:** 5-10 seconds (subsequent runs)
- **Send Message:** 1-3 seconds
- **Auto-Responder:** 5-15 seconds per message (with Claude API)

### LinkedIn
- **Strategy Generation:** 1-2 seconds
- **Post Generation:** <1 second per post
- **Calendar Generation:** 1-2 seconds
- **Lead Tracking:** <1 second per operation
- **All operations:** Instant (no API calls required)

---

## Security

### Gmail
- OAuth 2.0 authentication
- Token stored locally
- No password storage
- Scopes limited to necessary permissions

### WhatsApp
- Session stored locally in `.wwebjs_auth/`
- No credentials stored
- All data local-first
- Optional Claude API (can work without)

### LinkedIn
- No authentication required
- All data stored locally
- No API calls or external services
- Complete privacy and control

---

## Extending the System

### Add New Gmail Skill

1. Create skill definition: `skills/gmail/commands/new-skill.skill`
2. Create implementation: `skills/gmail/scripts/new_skill.py`
3. Update `skills/gmail/README.md`
4. Test thoroughly

### Add New WhatsApp Skill

1. Create skill definition: `skills/whatsapp/commands/new-skill.skill`
2. Create implementation: `skills/whatsapp/scripts/new_skill.py`
3. Update `skills/whatsapp/README.md`
4. Test with Node.js backend

### Customize LinkedIn Content

**Modify Post Templates:**
Edit `linkedin/linkedin_post_generator.py` to add your own post templates and styles.

**Adjust Posting Schedule:**
Edit `linkedin/linkedin_calendar_generator.py` to change posting times and frequency.

**Customize Strategy:**
Edit `linkedin/linkedin_strategy_generator.py` to modify strategy sections and metrics.

### Customize AI Responses

Edit `whatsapp-node/whatsapp_assistant.py`:
- Modify `system_prompt` for personality
- Adjust `max_tokens` for response length
- Change `temperature` for creativity

---

## FAQ

**Q: Do I need Claude API key for WhatsApp?**
A: No. It works without API key using simple fallback responses. API key enables intelligent AI responses.

**Q: Can I use this for multiple Gmail accounts?**
A: Yes. Use different `credentials.json` and `token.json` files for each account.

**Q: Does WhatsApp work without Node.js backend?**
A: No. The Node.js backend is required for WhatsApp functionality.

**Q: Can I run WhatsApp auto-responder 24/7?**
A: Yes. Keep Node.js backend and auto-responder running. Consider using systemd or Docker for production.

**Q: Does LinkedIn automation post automatically?**
A: No. The tools generate content and calendars. You schedule and post manually or use LinkedIn's native scheduler.

**Q: Do I need LinkedIn API access?**
A: No. All LinkedIn tools work offline and generate content locally. No API required.

**Q: How long to see results from LinkedIn strategy?**
A: Month 1: 2-3 leads, Month 2: 5-7 leads, Month 3: 10+ leads with consistent execution.

**Q: How do I backup my data?**
A: Copy the entire `silver-tier/` folder. All data is in local files.

---

## What's Next?

### Immediate (Next 5 Minutes)

**Gmail:**
```bash
cd skills/gmail
python scripts/send_email.py
# Authenticate and send first email
```

**WhatsApp:**
```bash
cd whatsapp-node
npm start
# Scan QR code, then use skills
```

**LinkedIn:**
```bash
cd linkedin
python linkedin_strategy_generator.py --interactive
# Generate your content strategy
```

### Short Term (This Week)

1. Test all 8 Gmail/WhatsApp skills
2. Generate LinkedIn content strategy and calendar
3. Create first batch of LinkedIn posts
4. Customize AI assistant personality
5. Set up auto-responder for common queries

### Long Term (This Month)

1. Execute LinkedIn posting schedule consistently
2. Track and nurture LinkedIn leads
3. Add custom skills for your workflows
4. Integrate with other systems
5. Monitor and optimize performance

---

**You're ready. Start with any platform and explore the automation capabilities.**

```bash
# Quick start - Gmail
cd skills/gmail
python scripts/send_email.py

# Quick start - WhatsApp
cd whatsapp-node
npm start
# Then in another terminal:
cd skills/whatsapp
python scripts/send_message.py

# Quick start - LinkedIn
cd linkedin
python linkedin_strategy_generator.py --interactive
```

**Documentation:**
- Gmail & WhatsApp Skills: `skills/README.md` and `skills/SKILLS_SUMMARY.md`
- LinkedIn Automation: `linkedin/README.md`
- Complete Silver Tier Guide: This file

