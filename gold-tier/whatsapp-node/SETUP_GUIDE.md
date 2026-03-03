# WhatsApp Watcher System - Complete Setup Guide

## What Was Built

A complete WhatsApp automation system with:

1. **Node.js Backend** - Captures incoming messages and sends outgoing messages
2. **Python Watcher** - Monitors incoming messages continuously
3. **AI Assistant** - Generates intelligent responses (customizable)
4. **Message Sender** - Sends messages with retry logic
5. **State Management** - Logs all activity to whatsapp_state.json

## Files Created

```
whatsapp-node/
├── server.js                    # Node.js Express server
├── src/
│   ├── config/index.js         # Configuration
│   ├── services/whatsappService.js  # WhatsApp client (UPDATED with message listening)
│   └── routes/whatsapp.js      # API routes (UPDATED with message endpoints)
├── whatsapp_sender.py          # Send messages programmatically
├── whatsapp_assistant.py       # AI response generator
├── whatsapp_watcher.py         # Incoming message monitor
├── quick_start.py              # Interactive menu
├── whatsapp_state.json         # State and configuration
└── README.md                   # Full documentation
```

## Setup Instructions

### Step 1: Restart Node.js Server

**IMPORTANT:** You must restart the server to enable incoming message capture.

```bash
# Stop the current server (Ctrl+C in the terminal where it's running)

# Then restart it
cd whatsapp-node
npm start
```

You should see:
```
Server running on port 3000
WhatsApp authenticated successfully
WhatsApp client is ready!
```

### Step 2: Verify Server is Working

Test the new endpoints:

```bash
# Check status
curl http://localhost:3000/api/whatsapp/status

# Check incoming messages
curl http://localhost:3000/api/whatsapp/messages
```

### Step 3: Start the Watcher

**Option A: Interactive Menu (Recommended for first time)**
```bash
python quick_start.py
```

Choose option 1 to test all components, then option 3 to start the watcher.

**Option B: Direct Start**
```bash
python whatsapp_watcher.py
```

### Step 4: Test the System

1. Send a WhatsApp message to your authenticated number (923332455342)
2. Watch the watcher console - it should:
   - Detect the incoming message
   - Generate an AI response
   - Send the reply automatically (or ask for approval if human-in-the-loop is enabled)

## Configuration

Edit `whatsapp_state.json` to customize behavior:

```json
{
  "human_in_the_loop": false,        // Set to true to approve each reply
  "watcher_config": {
    "poll_interval_seconds": 5,      // How often to check for messages
    "auto_reply_enabled": true,      // Enable/disable auto-replies
    "process_group_messages": false  // Respond in group chats
  }
}
```

## Usage Examples

### Example 1: Auto-Responder (No Approval)

```bash
# Edit whatsapp_state.json
{
  "human_in_the_loop": false,
  "watcher_config": {
    "auto_reply_enabled": true
  }
}

# Start watcher
python whatsapp_watcher.py
```

Now any message sent to you will get an automatic AI response.

### Example 2: Human-in-the-Loop (Approval Required)

```bash
# Edit whatsapp_state.json
{
  "human_in_the_loop": true,
  "watcher_config": {
    "auto_reply_enabled": true
  }
}

# Start watcher
python whatsapp_watcher.py
```

The watcher will ask for your approval before sending each reply.

### Example 3: Manual Message Sending

```python
from whatsapp_sender import WhatsAppSender

sender = WhatsAppSender()
sender.send_message("923332455342", "Hello from Python!")
```

### Example 4: Single Iteration (No Continuous Monitoring)

```python
from whatsapp_watcher import WhatsAppWatcher

watcher = WhatsAppWatcher()
processed = watcher.run_once()  # Process messages once and exit
print(f"Processed {processed} messages")
```

## Customizing the AI Assistant

The default assistant uses simple rule-based responses. To add real AI:

### OpenAI Integration

1. Install: `pip install openai`
2. Edit `whatsapp_assistant.py`:

```python
def generate_response(self, message_data):
    # Replace the call to _generate_simple_response with:
    return self._generate_openai_response(message_body, sender_name, context)
```

3. Add your API key in the `_generate_openai_response` method

### Anthropic Claude Integration

1. Install: `pip install anthropic`
2. Similar process as OpenAI

### Local LLM (Ollama)

1. Install Ollama: https://ollama.ai
2. Run: `ollama run llama2`
3. Integrate with requests to `http://localhost:11434/api/generate`

## Monitoring and Logs

All activity is logged to `whatsapp_state.json`:

```python
# View logs
import json

with open('whatsapp_state.json', 'r') as f:
    state = json.load(f)

# Incoming messages
print(state['incoming_messages'])

# Pending/sent replies
print(state['pending_replies'])

# Sent messages
print(state['message_log'])
```

## Troubleshooting

### Server not responding
- Make sure you restarted the Node.js server after the updates
- Check if port 3000 is available

### No messages detected
- Send a test message to your WhatsApp number
- Check server console for "📨 New message from..."
- Verify with: `curl http://localhost:3000/api/whatsapp/messages`

### Watcher not responding
- Check `auto_reply_enabled` is true in whatsapp_state.json
- Verify Node.js server is running
- Check for errors in watcher console

### Messages not sending
- Verify WhatsApp is authenticated: `curl http://localhost:3000/api/whatsapp/status`
- Check number format (include country code, no +)

## Next Steps

1. **Restart your Node.js server** (most important!)
2. Test the system by sending yourself a message
3. Customize the AI assistant with your preferred backend
4. Configure human-in-the-loop based on your needs
5. Monitor logs in whatsapp_state.json

## Support

- Check README.md for full API documentation
- Use quick_start.py for interactive testing
- All components are modular and can be used independently
