const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const config = require('../config');

class WhatsAppService {
  constructor() {
    this.client = null;
    this.isReady = false;
    this.qrCode = null;
    this.incomingMessages = []; // Store incoming messages
    this.maxStoredMessages = 100; // Limit stored messages
  }

  initialize() {
    this.client = new Client({
      authStrategy: new LocalAuth({
        dataPath: config.whatsapp.sessionPath
      }),
      puppeteer: {
        args: config.whatsapp.puppeteerArgs
      }
    });

    this.client.on('qr', (qr) => {
      console.log('QR Code received. Scan with WhatsApp:');
      qrcode.generate(qr, { small: true });
      this.qrCode = qr;
    });

    this.client.on('ready', () => {
      console.log('WhatsApp client is ready!');
      this.isReady = true;
      this.qrCode = null;
    });

    this.client.on('authenticated', () => {
      console.log('WhatsApp authenticated successfully');
    });

    this.client.on('auth_failure', (msg) => {
      console.error('Authentication failure:', msg);
      this.isReady = false;
    });

    this.client.on('disconnected', (reason) => {
      console.log('WhatsApp client disconnected:', reason);
      this.isReady = false;
    });

    // Listen for incoming messages
    this.client.on('message', async (message) => {
      try {
        const contact = await message.getContact();
        const chat = await message.getChat();

        const messageData = {
          id: message.id.id,
          from: message.from,
          fromName: contact.pushname || contact.name || message.from,
          body: message.body,
          timestamp: message.timestamp,
          isGroup: chat.isGroup,
          chatName: chat.name,
          type: message.type,
          hasMedia: message.hasMedia,
          processed: false,
          receivedAt: new Date().toISOString()
        };

        // Store message
        this.incomingMessages.push(messageData);

        // Limit stored messages
        if (this.incomingMessages.length > this.maxStoredMessages) {
          this.incomingMessages.shift();
        }

        console.log(`📨 New message from ${messageData.fromName}: ${message.body.substring(0, 50)}...`);
      } catch (error) {
        console.error('Error processing incoming message:', error);
      }
    });

    this.client.initialize();
  }

  async sendMessage(number, message) {
    if (!this.isReady) {
      throw new Error('WhatsApp client is not ready');
    }

    // Format number to WhatsApp format (remove special chars, add country code if needed)
    const formattedNumber = number.replace(/[^\d]/g, '');
    const chatId = `${formattedNumber}@c.us`;

    try {
      const response = await this.client.sendMessage(chatId, message);
      return {
        success: true,
        messageId: response.id.id,
        timestamp: response.timestamp
      };
    } catch (error) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  getStatus() {
    return {
      isReady: this.isReady,
      hasQR: !!this.qrCode,
      qrCode: this.qrCode
    };
  }

  async getClientInfo() {
    if (!this.isReady) {
      throw new Error('WhatsApp client is not ready');
    }

    const info = this.client.info;
    return {
      number: info.wid.user,
      name: info.pushname,
      platform: info.platform
    };
  }

  getIncomingMessages(unprocessedOnly = false) {
    if (unprocessedOnly) {
      return this.incomingMessages.filter(msg => !msg.processed);
    }
    return this.incomingMessages;
  }

  markMessageProcessed(messageId) {
    const message = this.incomingMessages.find(msg => msg.id === messageId);
    if (message) {
      message.processed = true;
      return true;
    }
    return false;
  }

  clearProcessedMessages() {
    this.incomingMessages = this.incomingMessages.filter(msg => !msg.processed);
    return this.incomingMessages.length;
  }

  async getContacts() {
    if (!this.isReady) {
      throw new Error('WhatsApp client is not ready');
    }

    try {
      // Get all chats (recent conversations)
      const chats = await this.client.getChats();

      // Filter and format contacts with error handling
      const contactPromises = chats
        .filter(chat => !chat.isGroup) // Only individual contacts
        .slice(0, 100) // Limit to 100 most recent
        .map(async (chat) => {
          try {
            const contact = await chat.getContact();
            return {
              id: chat.id._serialized || chat.id,
              name: contact.pushname || contact.name || chat.name || 'Unknown',
              number: contact.number || chat.id.user || 'Unknown',
              isMyContact: contact.isMyContact || false,
              lastMessageTime: chat.timestamp || 0
            };
          } catch (err) {
            // Skip contacts that fail to load
            console.error(`Error loading contact: ${err.message}`);
            return null;
          }
        });

      const contacts = (await Promise.all(contactPromises))
        .filter(contact => contact !== null); // Remove failed contacts

      // Sort by last message time (most recent first)
      contacts.sort((a, b) => b.lastMessageTime - a.lastMessageTime);

      return contacts;
    } catch (error) {
      console.error('Error in getContacts:', error);
      throw new Error(`Failed to get contacts: ${error.message}`);
    }
  }
}

module.exports = new WhatsAppService();
