const express = require('express');
const router = express.Router();
const whatsappService = require('../services/whatsappService');

// Get WhatsApp status
router.get('/status', (req, res) => {
  try {
    const status = whatsappService.getStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get client info
router.get('/info', async (req, res) => {
  try {
    const info = await whatsappService.getClientInfo();
    res.json(info);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Send message
router.post('/send', async (req, res, next) => {
  try {
    const { number, message } = req.body;

    if (!number || !message) {
      return res.status(400).json({
        error: 'Missing required fields: number and message'
      });
    }

    console.log(`Attempting to send message to ${number}`);
    const result = await whatsappService.sendMessage(number, message);
    console.log('Message sent successfully:', result);
    res.json(result);
  } catch (error) {
    console.error('Error in send route:', error);
    res.status(400).json({ error: error.message });
  }
});

// Get incoming messages
router.get('/messages', (req, res) => {
  try {
    const unprocessedOnly = req.query.unprocessed === 'true';
    const messages = whatsappService.getIncomingMessages(unprocessedOnly);
    res.json({
      count: messages.length,
      messages: messages
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Mark message as processed
router.post('/messages/:messageId/processed', (req, res) => {
  try {
    const { messageId } = req.params;
    const success = whatsappService.markMessageProcessed(messageId);

    if (success) {
      res.json({ success: true, messageId });
    } else {
      res.status(404).json({ error: 'Message not found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Clear processed messages
router.delete('/messages/processed', (req, res) => {
  try {
    const remaining = whatsappService.clearProcessedMessages();
    res.json({
      success: true,
      remainingMessages: remaining
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get contacts
router.get('/contacts', async (req, res) => {
  try {
    const contacts = await whatsappService.getContacts();
    res.json({
      count: contacts.length,
      contacts: contacts
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
