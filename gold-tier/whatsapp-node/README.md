# WhatsApp Node Service

Production-ready WhatsApp messaging service with AI-powered auto-responder using whatsapp-web.js and Express API.

## Features

- QR code authentication with session persistence
- RESTful API endpoints for sending messages
- **Incoming message monitoring and capture**
- **AI-powered auto-responder with customizable assistant**
- **Human-in-the-loop approval for replies (configurable)**
- **Message logging and state management**
- Send WhatsApp messages programmatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WhatsApp Web (Browser)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Node.js Backend (Express + whatsapp-web.js)     │
│  • Captures incoming messages                                │
│  • Sends outgoing messages                                   │
│  • Manages session authentication                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ whatsapp_watcher │  │ whatsapp_sender  │                │
│  │ (Monitor & Auto) │  │ (Send Messages)  │                │
│  └────────┬─────────┘  └──────────────────┘                │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │whatsapp_assistant│                                       │
│  │  (AI Responses)  │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              whatsapp_state.json
         (State, Logs, Configuration)
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Start the service:
```bash
npm start
```

4. Scan the QR code displayed in the terminal with WhatsApp mobile app

## API Endpoints

### Message Sending

#### GET /api/whatsapp/status
Check WhatsApp client status and get QR code if needed.

**Response:**
```json
{
  "isReady": true,
  "hasQR": false,
  "qrCode": null
}
```

#### GET /api/whatsapp/info
Get authenticated WhatsApp account information.

**Response:**
```json
{
  "number": "1234567890",
  "name": "Your Name",
  "platform": "android"
}
```

#### POST /api/whatsapp/send
Send a WhatsApp message.

**Request Body:**
```json
{
  "number": "1234567890",
  "message": "Hello from WhatsApp API!"
}
```

**Response:**
```json
{
  "success": true,
  "messageId": "...",
  "timestamp": 1234567890
}
```

### Message Monitoring

#### GET /api/whatsapp/messages
Get incoming messages.

**Query Parameters:**
- `unprocessed=true` - Only return unprocessed messages

**Response:**
```json
{
  "count": 2,
  "messages": [
    {
      "id": "msg123",
      "from": "1234567890@c.us",
      "fromName": "John Doe",
      "body": "Hello!",
      "timestamp": 1234567890,
      "isGroup": false,
      "processed": false
    }
  ]
}
```

#### POST /api/whatsapp/messages/:messageId/processed
Mark a message as processed.

**Response:**
```json
{
  "success": true,
  "messageId": "msg123"
}
```

#### DELETE /api/whatsapp/messages/processed
Clear all processed messages from memory.

**Response:**
```json
{
  "success": true,
  "remainingMessages": 5
}
```

## Project Structure

```
whatsapp-node/
├── src/
│   ├── config/
│   │   └── index.js          # Configuration
│   ├── services/
│   │   └── whatsappService.js # WhatsApp client logic
│   └── routes/
│       └── whatsapp.js        # API routes
├── server.js                  # Entry point
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## Python Wrapper

A complete Python automation system is provided for AI-powered message handling.

### Components

1. **whatsapp_sender.py** - Send messages programmatically
2. **whatsapp_assistant.py** - AI response generation (customizable)
3. **whatsapp_watcher.py** - Monitor incoming messages and auto-respond
4. **quick_start.py** - Interactive menu for easy setup

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

**Option 1: Interactive Menu**
```bash
python quick_start.py
```

**Option 2: Start Watcher Directly**
```bash
python whatsapp_watcher.py
```

**Option 3: Send Messages Only**
```python
from whatsapp_sender import WhatsAppSender

sender = WhatsAppSender()
sender.send_message("923332455342", "Hello from Python!")
```

### Watcher Usage

The watcher continuously monitors incoming messages and generates AI responses:

```python
from whatsapp_watcher import WhatsAppWatcher

# Start continuous monitoring
watcher = WhatsAppWatcher()
watcher.start()  # Press Ctrl+C to stop

# Or run single iteration
watcher.run_once()
```

### AI Assistant Customization

The assistant uses simple rule-based responses by default. To integrate with real AI:

**OpenAI Integration:**
```python
# In whatsapp_assistant.py, uncomment and configure:
def _generate_openai_response(self, message, sender_name, context):
    import openai
    openai.api_key = "your-key"
    # ... implementation
```

**Anthropic Claude:**
```python
def _generate_claude_response(self, message, sender_name, context):
    import anthropic
    client = anthropic.Anthropic(api_key="your-key")
    # ... implementation
```

**Local LLM (Ollama):**
```python
def _generate_ollama_response(self, message, sender_name, context):
    import requests
    response = requests.post("http://localhost:11434/api/generate", ...)
    # ... implementation
```

### Configuration (whatsapp_state.json)

```json
{
  "api_endpoint": "http://localhost:3000/api/whatsapp",
  "human_in_the_loop": false,
  "watcher_config": {
    "poll_interval_seconds": 5,
    "auto_reply_enabled": true,
    "process_group_messages": false
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay_seconds": 2
  }
}
```

**Configuration Options:**
- `human_in_the_loop`: Require approval before sending replies
- `auto_reply_enabled`: Enable/disable automatic responses
- `poll_interval_seconds`: How often to check for new messages
- `process_group_messages`: Whether to respond in group chats

## Testing

### Test Node.js API directly:
```bash
# Check status
curl http://localhost:3000/api/whatsapp/status

# Get account info
curl http://localhost:3000/api/whatsapp/info

# Send message
curl -X POST http://localhost:3000/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"number": "923332455342", "message": "Test message"}'
```

### Test Python wrapper:
```bash
python example_usage.py
```

## Notes

- Session data is stored in `.wwebjs_auth/` directory
- First run requires QR code scan
- Subsequent runs will use saved session
- Number format: Include country code without '+' (e.g., 923332455342)
- Python wrapper logs all messages to `whatsapp_state.json`
- Human-in-the-loop can be toggled via `set_human_in_the_loop()`
