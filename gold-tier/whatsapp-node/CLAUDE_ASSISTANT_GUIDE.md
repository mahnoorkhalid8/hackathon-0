# WhatsApp Assistant with Claude API - Setup Guide

## Overview

The WhatsApp Assistant now uses Anthropic's Claude API to generate intelligent, contextual responses to incoming messages. This provides much better conversation quality compared to simple rule-based responses.

## Features

✅ **Claude 3.5 Sonnet Integration** - Uses the latest Claude model for intelligent responses
✅ **Conversation History** - Maintains context across multiple messages per contact
✅ **Reply Logging** - All generated replies logged to whatsapp_state.json for approval tracking
✅ **Fallback Responses** - Graceful degradation if API is unavailable
✅ **Error Handling** - Robust error handling for API failures
✅ **Customizable Personality** - Adjust system prompt to change assistant behavior

## Setup Instructions

### Step 1: Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### Step 2: Configure Environment

Add your API key to the `.env` file:

```bash
# Open .env file
nano .env  # or use any text editor

# Add this line:
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

**Important:** Never commit your `.env` file to git. It's already in `.gitignore`.

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For HTTP API calls
- `anthropic` - Official Anthropic Python SDK

### Step 4: Test the Assistant

```bash
python whatsapp_assistant.py
```

You should see:
```
🤖 Testing WhatsApp Assistant with Claude API

Incoming: Hello! Can you help me understand how AI works?

✅ Response generated:
   To: 923332455342
   Message: [Claude's intelligent response]
```

If API key is not set, you'll see:
```
⚠️  WARNING: ANTHROPIC_API_KEY not set. Using fallback responses.
```

## Usage

### Basic Usage (Integrated with Watcher)

The assistant is automatically used by `whatsapp_watcher.py`:

```bash
# Start the watcher (uses Claude assistant automatically)
python whatsapp_watcher.py
```

### Standalone Usage

```python
from whatsapp_assistant import WhatsAppAssistant

# Initialize assistant
assistant = WhatsAppAssistant()

# Process a message
message_data = {
    "id": "msg123",
    "from": "1234567890@c.us",
    "fromName": "John Doe",
    "body": "What's the weather like?",
    "timestamp": 1234567890,
    "isGroup": False,
    "type": "chat",
    "hasMedia": False
}

# Generate response
response = assistant.process_message(message_data)

if response:
    print(f"Reply: {response['message']}")
    print(f"To: {response['recipient']}")
```

## Customization

### Change AI Personality

Edit `whatsapp_assistant.py` and modify the `system_prompt`:

```python
self.system_prompt = """You are a professional customer service assistant.
Your responses should be:
- Professional and courteous
- Detailed and informative
- Solution-oriented
- Empathetic to customer concerns

Always maintain a helpful and positive tone."""
```

### Adjust Response Length

```python
self.max_tokens = 300  # Shorter responses
# or
self.max_tokens = 1000  # Longer, more detailed responses
```

### Change Temperature (Creativity)

```python
self.temperature = 0.3  # More focused and deterministic
# or
self.temperature = 1.0  # More creative and varied
```

### Use Different Claude Model

```python
self.model = "claude-3-opus-20240229"  # Most capable
# or
self.model = "claude-3-sonnet-20240229"  # Balanced
# or
self.model = "claude-3-haiku-20240307"  # Fastest, most economical
```

## Generated Replies Log

All AI-generated replies are logged to `whatsapp_state.json` under `generated_replies`:

```json
{
  "generated_replies": [
    {
      "id": "reply_1234567890.123",
      "original_message_id": "msg123",
      "from": "1234567890@c.us",
      "fromName": "John Doe",
      "original_message": "Hello, how are you?",
      "generated_reply": "Hello John! I'm doing great, thanks for asking...",
      "status": "pending_approval",
      "generated_at": "2024-02-16T10:30:00",
      "model": "claude-3-5-sonnet-20241022"
    }
  ]
}
```

### View Generated Replies

```python
from whatsapp_assistant import WhatsAppAssistant

assistant = WhatsAppAssistant()

# Get all pending replies
pending = assistant.get_generated_replies(status="pending_approval")
for reply in pending:
    print(f"{reply['fromName']}: {reply['generated_reply']}")

# Update reply status
assistant.update_reply_status("reply_1234567890.123", "approved")
```

## Conversation History

The assistant maintains conversation history per contact (in-memory):

- Stores last 10 messages per contact
- Provides context to Claude for better responses
- Automatically managed (no manual intervention needed)

Example conversation flow:
```
User: "What's the capital of France?"
Claude: "The capital of France is Paris."

User: "What's the population?"
Claude: "Paris has a population of approximately 2.2 million people in the city proper..."
```

Claude remembers the context (Paris) from the previous message.

## Error Handling

The assistant handles various error scenarios:

1. **API Key Not Set** - Falls back to simple rule-based responses
2. **API Connection Error** - Retries with fallback
3. **API Rate Limit** - Falls back gracefully
4. **Invalid Response** - Uses fallback response

All errors are logged to console for debugging.

## Cost Considerations

Claude API pricing (as of 2024):
- **Claude 3.5 Sonnet**: ~$3 per million input tokens, ~$15 per million output tokens
- **Claude 3 Haiku**: ~$0.25 per million input tokens, ~$1.25 per million output tokens

Typical WhatsApp message costs:
- Short message (50 tokens): ~$0.0002 with Sonnet
- Medium message (200 tokens): ~$0.0008 with Sonnet

For high-volume usage, consider:
1. Using Claude 3 Haiku (much cheaper)
2. Limiting conversation history
3. Reducing max_tokens
4. Adding message filtering

## Troubleshooting

### "ANTHROPIC_API_KEY not set" Warning

**Solution:** Add your API key to `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### "API Connection Error"

**Possible causes:**
- No internet connection
- Firewall blocking API requests
- Invalid API key

**Solution:** Check internet connection and verify API key is correct.

### "API Rate Limit Exceeded"

**Solution:**
- Wait a few minutes before retrying
- Consider upgrading your Anthropic plan
- Use Claude 3 Haiku for higher throughput

### Responses Are Too Long/Short

**Solution:** Adjust `max_tokens` in `whatsapp_assistant.py`:
```python
self.max_tokens = 300  # Shorter responses
```

### Assistant Not Responding to Group Messages

**Expected behavior:** Group messages are filtered by default.

**Solution:** Enable in `whatsapp_state.json`:
```json
{
  "watcher_config": {
    "process_group_messages": true
  }
}
```

## Testing Without API Key

The assistant works without an API key using fallback responses:

```bash
# Don't set ANTHROPIC_API_KEY
python whatsapp_assistant.py
```

This is useful for:
- Testing the system architecture
- Development without API costs
- Fallback when API is unavailable

## Integration with Watcher

The watcher automatically uses the Claude assistant:

```python
# In whatsapp_watcher.py
assistant = WhatsAppAssistant()  # Automatically loads Claude

# Process incoming message
reply = assistant.process_message(message_data)

# Send reply
sender.send_message(reply['recipient'], reply['message'])
```

## Best Practices

1. **Set Appropriate System Prompt** - Define clear personality and behavior
2. **Monitor Costs** - Check Anthropic dashboard regularly
3. **Test Thoroughly** - Test with various message types before production
4. **Use Human-in-the-Loop** - Enable approval for important conversations
5. **Log Everything** - Keep logs for debugging and improvement
6. **Handle Errors Gracefully** - Always have fallback responses
7. **Respect Privacy** - Don't log sensitive information

## Next Steps

1. ✅ Set up your Claude API key
2. ✅ Test the assistant standalone
3. ✅ Customize the system prompt for your use case
4. ✅ Start the watcher with Claude integration
5. ✅ Monitor generated replies in whatsapp_state.json
6. ✅ Adjust settings based on response quality

## Support

For issues with:
- **Claude API**: https://docs.anthropic.com/
- **WhatsApp Integration**: Check SETUP_GUIDE.md
- **Python Code**: Review whatsapp_assistant.py comments

Happy automating! 🤖
