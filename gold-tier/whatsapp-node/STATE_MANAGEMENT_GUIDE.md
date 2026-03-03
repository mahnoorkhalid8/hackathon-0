# State Management System - Complete Guide

## Overview

The state management system provides thread-safe operations for managing WhatsApp session state, message tracking, and statistics. It ensures **no re-authentication is needed** unless the session becomes invalid.

## Key Features

✅ **Session Management** - Tracks authentication status and prevents unnecessary QR scans
✅ **Thread-Safe Operations** - Safe for concurrent access from multiple components
✅ **Message Lifecycle Tracking** - Tracks messages through their entire lifecycle
✅ **Statistics** - Real-time statistics on message flow
✅ **Automatic Timestamps** - All operations are timestamped automatically
✅ **Backup & Export** - Easy state backup and export functionality

## State File Structure

```json
{
  "session": {
    "authenticated": true,
    "last_authenticated": "2024-02-16T17:30:00",
    "session_valid": true,
    "session_path": ".wwebjs_auth",
    "requires_qr": false,
    "last_validation": "2024-02-16T17:30:00",
    "validation_interval_minutes": 30
  },
  "account_info": {
    "number": "923332455342",
    "name": "Mahnoor",
    "platform": "iphone",
    "last_updated": "2024-02-16T17:30:00"
  },
  "messages": {
    "incoming": [],
    "pending_approval": [],
    "approved": [],
    "rejected": [],
    "sent": [],
    "failed": []
  },
  "statistics": {
    "total_incoming": 0,
    "total_sent": 0,
    "total_failed": 0,
    "total_approved": 0,
    "total_rejected": 0,
    "last_message_received": null,
    "last_message_sent": null
  }
}
```

## Usage

### Basic Usage

```python
from state_manager import StateManager, MessageStatus

# Initialize
manager = StateManager()

# Check session status
if manager.is_session_valid():
    print("Session is valid, no QR scan needed")
else:
    print("Session invalid, QR scan required")
```

### Session Management

```python
# Update session after authentication
manager.update_session_status(
    authenticated=True,
    account_info={
        "number": "923332455342",
        "name": "Mahnoor",
        "platform": "iphone"
    }
)

# Check if QR scan is required
if manager.requires_qr_scan():
    print("Please scan QR code")
else:
    print("Using existing session")

# Get session info
session_info = manager.get_session_info()
print(f"Last authenticated: {session_info['last_authenticated']}")

# Mark session as invalid (forces re-authentication)
manager.mark_session_invalid(reason="Connection lost")
```

### Message Management

```python
# Add incoming message
manager.add_message(
    {
        "id": "msg123",
        "from": "1234567890@c.us",
        "fromName": "John Doe",
        "body": "Hello!"
    },
    MessageStatus.INCOMING
)

# Move message through lifecycle
manager.move_message("msg123", MessageStatus.INCOMING, MessageStatus.PENDING_APPROVAL)
manager.move_message("msg123", MessageStatus.PENDING_APPROVAL, MessageStatus.APPROVED)
manager.move_message("msg123", MessageStatus.APPROVED, MessageStatus.SENT)

# Get messages by status
pending = manager.get_messages(MessageStatus.PENDING_APPROVAL)
sent = manager.get_messages(MessageStatus.SENT, limit=10)

# Clear messages
manager.clear_messages(MessageStatus.SENT)
```

### Statistics

```python
# Get statistics
stats = manager.get_statistics()
print(f"Total incoming: {stats['total_incoming']}")
print(f"Total sent: {stats['total_sent']}")
print(f"Success rate: {stats['total_sent'] / stats['total_incoming'] * 100}%")

# Reset statistics
manager.reset_statistics()
```

### Configuration

```python
# Get configuration
human_approval = manager.get_config('human_in_the_loop')

# Set configuration
manager.set_config('human_in_the_loop', True)

# Update multiple configs
manager.update_config({
    'human_in_the_loop': False,
    'watcher_config': {
        'poll_interval_seconds': 10,
        'auto_reply_enabled': True
    }
})
```

### Backup & Export

```python
# Create backup
backup_file = manager.backup_state()
print(f"Backup created: {backup_file}")

# Export to custom location
manager.export_state("backup/state_2024_02_16.json")

# Get full state
full_state = manager.get_full_state()
```

## Integration with Existing Components

### Integration with whatsapp_sender.py

```python
from state_manager import StateManager, MessageStatus
from whatsapp_sender import WhatsAppSender

manager = StateManager()
sender = WhatsAppSender()

# Check session before sending
if not manager.is_session_valid():
    print("Session invalid, cannot send messages")
    exit(1)

# Send message and track it
message_data = {
    "id": "msg456",
    "recipient": "923332455342",
    "body": "Hello from state manager!"
}

# Add to pending
manager.add_message(message_data, MessageStatus.PENDING_APPROVAL)

# Send
success = sender.send_message(message_data['recipient'], message_data['body'])

# Update status
if success:
    manager.move_message("msg456", MessageStatus.PENDING_APPROVAL, MessageStatus.SENT)
else:
    manager.move_message("msg456", MessageStatus.PENDING_APPROVAL, MessageStatus.FAILED)
```

### Integration with whatsapp_assistant.py

```python
from state_manager import StateManager, MessageStatus
from whatsapp_assistant import WhatsAppAssistant

manager = StateManager()
assistant = WhatsAppAssistant()

# Process incoming message
incoming_msg = {
    "id": "msg789",
    "from": "1234567890@c.us",
    "fromName": "Jane Doe",
    "body": "What's the weather?",
    "timestamp": 1234567890,
    "isGroup": False
}

# Track incoming message
manager.add_message(incoming_msg, MessageStatus.INCOMING)

# Generate response
response = assistant.process_message(incoming_msg)

if response:
    # Add to pending approval
    reply_data = {
        "id": f"reply_{incoming_msg['id']}",
        "recipient": response['recipient'],
        "body": response['message'],
        "original_message_id": incoming_msg['id']
    }

    manager.add_message(reply_data, MessageStatus.PENDING_APPROVAL)

    # If human approval required
    if manager.get_config('human_in_the_loop'):
        # Wait for approval...
        # Then move to approved
        manager.move_message(reply_data['id'], MessageStatus.PENDING_APPROVAL, MessageStatus.APPROVED)
```

### Integration with whatsapp_watcher.py

```python
from state_manager import StateManager, MessageStatus
from whatsapp_watcher import WhatsAppWatcher

manager = StateManager()
watcher = WhatsAppWatcher()

# Before starting watcher, validate session
if not manager.is_session_valid():
    print("Session invalid. Please authenticate first.")
    exit(1)

print("Session valid. Starting watcher...")

# Update session validation periodically
def validate_session():
    # Check with backend
    status = watcher.sender.get_account_info()

    if status:
        manager.update_session_status(
            authenticated=True,
            account_info=status
        )
    else:
        manager.mark_session_invalid(reason="Backend not responding")

# Run watcher with session validation
watcher.start()
```

## Message Lifecycle

```
INCOMING → PENDING_APPROVAL → APPROVED → SENT
                ↓
            REJECTED
                ↓
            FAILED (if send fails)
```

### Lifecycle Example

```python
# 1. Message arrives
manager.add_message(msg, MessageStatus.INCOMING)

# 2. Needs approval
manager.move_message(msg_id, MessageStatus.INCOMING, MessageStatus.PENDING_APPROVAL)

# 3a. Approved
manager.move_message(msg_id, MessageStatus.PENDING_APPROVAL, MessageStatus.APPROVED)

# 3b. Or rejected
manager.move_message(msg_id, MessageStatus.PENDING_APPROVAL, MessageStatus.REJECTED)

# 4. Send (if approved)
manager.move_message(msg_id, MessageStatus.APPROVED, MessageStatus.SENT)

# 4b. Or failed
manager.move_message(msg_id, MessageStatus.APPROVED, MessageStatus.FAILED)
```

## Session Validation

The state manager automatically validates sessions based on:

1. **Authentication Status** - Is the session authenticated?
2. **Session Validity** - Is the session marked as valid?
3. **Validation Interval** - Has the session been validated recently?

```python
# Session is valid if:
# 1. authenticated = true
# 2. session_valid = true
# 3. last_validation < validation_interval_minutes

if manager.is_session_valid():
    # Use existing session
    pass
else:
    # Re-authenticate required
    if manager.requires_qr_scan():
        print("Please scan QR code")
```

### Preventing Re-Authentication

The system prevents unnecessary QR scans by:

1. Storing session state in `.wwebjs_auth/` directory
2. Tracking authentication status in state file
3. Validating session periodically (default: 30 minutes)
4. Only requiring QR when session is explicitly invalid

```python
# Session remains valid across restarts
# No QR scan needed if:
# - .wwebjs_auth/ directory exists
# - session.authenticated = true
# - session.session_valid = true
# - last_validation is recent
```

## Thread Safety

All operations are thread-safe using Python's `threading.Lock`:

```python
# Safe to call from multiple threads
thread1 = threading.Thread(target=lambda: manager.add_message(msg1, MessageStatus.INCOMING))
thread2 = threading.Thread(target=lambda: manager.add_message(msg2, MessageStatus.INCOMING))

thread1.start()
thread2.start()
thread1.join()
thread2.join()

# No race conditions or data corruption
```

## Best Practices

1. **Always Check Session** - Check `is_session_valid()` before operations
2. **Update Session Regularly** - Validate session every 30 minutes
3. **Track All Messages** - Use message lifecycle for complete tracking
4. **Backup Regularly** - Create backups before major operations
5. **Monitor Statistics** - Use statistics to track system health
6. **Handle Failures** - Always move failed messages to FAILED status

## Error Handling

```python
try:
    # Attempt operation
    manager.add_message(msg, MessageStatus.INCOMING)
except Exception as e:
    print(f"Error: {e}")
    # Session might be corrupted
    manager.mark_session_invalid(reason=str(e))
```

## Troubleshooting

### Issue: "Session invalid" after restart

**Cause:** Session validation expired or `.wwebjs_auth/` deleted

**Solution:**
```python
# Re-authenticate
manager.update_session_status(authenticated=True, account_info={...})
```

### Issue: Messages not tracked

**Cause:** Not using StateManager in components

**Solution:** Integrate StateManager into all components (see integration examples above)

### Issue: State file corrupted

**Cause:** Concurrent writes without lock or manual editing

**Solution:**
```python
# Restore from backup
import shutil
shutil.copy("whatsapp_state_backup_20240216.json", "whatsapp_state.json")
```

## API Reference

### StateManager Class

#### Session Methods
- `is_session_valid()` - Check if session is valid
- `update_session_status(authenticated, account_info)` - Update session
- `mark_session_invalid(reason)` - Invalidate session
- `requires_qr_scan()` - Check if QR scan needed
- `get_session_info()` - Get session information

#### Message Methods
- `add_message(message_data, status)` - Add message
- `get_messages(status, limit)` - Get messages by status
- `move_message(message_id, from_status, to_status)` - Move message
- `clear_messages(status)` - Clear messages

#### Statistics Methods
- `get_statistics()` - Get statistics
- `reset_statistics()` - Reset statistics

#### Configuration Methods
- `get_config(key)` - Get configuration value
- `set_config(key, value)` - Set configuration value
- `update_config(updates)` - Update multiple configs

#### Utility Methods
- `get_full_state()` - Get complete state
- `export_state(output_file)` - Export state
- `backup_state()` - Create backup

### MessageStatus Enum
- `INCOMING` - Newly received message
- `PENDING_APPROVAL` - Awaiting human approval
- `APPROVED` - Approved for sending
- `REJECTED` - Rejected by human
- `SENT` - Successfully sent
- `FAILED` - Failed to send

## Complete Example

```python
from state_manager import StateManager, MessageStatus
from whatsapp_sender import WhatsAppSender
from whatsapp_assistant import WhatsAppAssistant

# Initialize
manager = StateManager()
sender = WhatsAppSender()
assistant = WhatsAppAssistant()

# Validate session
if not manager.is_session_valid():
    print("Session invalid. Please authenticate.")
    exit(1)

# Process incoming message
incoming = {
    "id": "msg001",
    "from": "923332455342@c.us",
    "fromName": "User",
    "body": "Hello!"
}

# Track incoming
manager.add_message(incoming, MessageStatus.INCOMING)

# Generate response
response = assistant.process_message(incoming)

if response:
    reply = {
        "id": "reply_001",
        "recipient": response['recipient'],
        "body": response['message']
    }

    # Add to pending
    manager.add_message(reply, MessageStatus.PENDING_APPROVAL)

    # Approve (or wait for human approval)
    manager.move_message("reply_001", MessageStatus.PENDING_APPROVAL, MessageStatus.APPROVED)

    # Send
    success = sender.send_message(reply['recipient'], reply['body'])

    # Update status
    if success:
        manager.move_message("reply_001", MessageStatus.APPROVED, MessageStatus.SENT)
    else:
        manager.move_message("reply_001", MessageStatus.APPROVED, MessageStatus.FAILED)

# Check statistics
stats = manager.get_statistics()
print(f"Messages processed: {stats['total_incoming']}")
print(f"Messages sent: {stats['total_sent']}")
```

## Summary

The state management system provides:
- ✅ Session tracking to prevent re-authentication
- ✅ Complete message lifecycle management
- ✅ Thread-safe operations
- ✅ Real-time statistics
- ✅ Easy backup and export
- ✅ Simple integration with existing components

All requirements met:
- ✅ Store current session and metadata
- ✅ Track pending/approved messages with timestamps
- ✅ Read/write functions for Python scripts
- ✅ No QR scan unless session invalid
