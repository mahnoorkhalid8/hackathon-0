/**
 * Email Service Module
 *
 * Handles email sending using nodemailer with comprehensive error handling
 * and logging.
 *
 * @module emailService
 */

import nodemailer from 'nodemailer';
import logger from '../utils/logger.js';
import config from '../config/config.js';

class EmailService {
  constructor() {
    this.transporter = null;
    this.initialized = false;
  }

  /**
   * Initialize email transporter with configuration
   */
  async initialize() {
    try {
      // Create transporter based on configuration
      this.transporter = nodemailer.createTransport({
        host: config.email.host,
        port: config.email.port,
        secure: config.email.secure, // true for 465, false for other ports
        auth: {
          user: config.email.user,
          pass: config.email.password,
        },
        // Connection timeout
        connectionTimeout: 10000,
        // Socket timeout
        socketTimeout: 10000,
        // Retry configuration
        pool: true,
        maxConnections: 5,
        maxMessages: 100,
      });

      // Verify connection configuration
      await this.transporter.verify();

      this.initialized = true;
      logger.info('Email service initialized successfully', {
        host: config.email.host,
        port: config.email.port,
        user: config.email.user,
      });

      return true;
    } catch (error) {
      logger.error('Failed to initialize email service', {
        error: error.message,
        stack: error.stack,
      });
      throw new Error(`Email service initialization failed: ${error.message}`);
    }
  }

  /**
   * Send email
   *
   * @param {Object} emailData - Email data
   * @param {string} emailData.to - Recipient email address
   * @param {string} emailData.subject - Email subject
   * @param {string} emailData.body - Email body (HTML or plain text)
   * @param {string} [emailData.from] - Sender email (optional, uses default)
   * @param {string[]} [emailData.cc] - CC recipients (optional)
   * @param {string[]} [emailData.bcc] - BCC recipients (optional)
   * @param {Object[]} [emailData.attachments] - Attachments (optional)
   * @returns {Promise<Object>} Send result
   */
  async sendEmail(emailData) {
    if (!this.initialized) {
      throw new Error('Email service not initialized');
    }

    const startTime = Date.now();
    const requestId = this.generateRequestId();

    try {
      logger.info('Sending email', {
        requestId,
        to: emailData.to,
        subject: emailData.subject,
        from: emailData.from || config.email.from,
      });

      // Prepare mail options
      const mailOptions = {
        from: emailData.from || config.email.from,
        to: emailData.to,
        subject: emailData.subject,
        text: emailData.body, // Plain text body
        html: emailData.body, // HTML body (nodemailer auto-detects)
      };

      // Add optional fields
      if (emailData.cc) {
        mailOptions.cc = Array.isArray(emailData.cc)
          ? emailData.cc.join(',')
          : emailData.cc;
      }

      if (emailData.bcc) {
        mailOptions.bcc = Array.isArray(emailData.bcc)
          ? emailData.bcc.join(',')
          : emailData.bcc;
      }

      if (emailData.attachments) {
        mailOptions.attachments = emailData.attachments;
      }

      // Send email
      const info = await this.transporter.sendMail(mailOptions);

      const duration = Date.now() - startTime;

      logger.info('Email sent successfully', {
        requestId,
        messageId: info.messageId,
        to: emailData.to,
        subject: emailData.subject,
        duration: `${duration}ms`,
        response: info.response,
      });

      return {
        success: true,
        messageId: info.messageId,
        response: info.response,
        duration,
        requestId,
      };

    } catch (error) {
      const duration = Date.now() - startTime;

      logger.error('Failed to send email', {
        requestId,
        to: emailData.to,
        subject: emailData.subject,
        error: error.message,
        stack: error.stack,
        duration: `${duration}ms`,
      });

      return {
        success: false,
        error: error.message,
        errorCode: error.code || 'UNKNOWN_ERROR',
        duration,
        requestId,
      };
    }
  }

  /**
   * Send multiple emails (batch)
   *
   * @param {Object[]} emails - Array of email data objects
   * @returns {Promise<Object>} Batch send results
   */
  async sendBatch(emails) {
    if (!this.initialized) {
      throw new Error('Email service not initialized');
    }

    logger.info('Sending batch emails', {
      count: emails.length,
    });

    const results = [];
    let successCount = 0;
    let failureCount = 0;

    for (const email of emails) {
      const result = await this.sendEmail(email);
      results.push(result);

      if (result.success) {
        successCount++;
      } else {
        failureCount++;
      }
    }

    logger.info('Batch email send completed', {
      total: emails.length,
      success: successCount,
      failure: failureCount,
    });

    return {
      total: emails.length,
      success: successCount,
      failure: failureCount,
      results,
    };
  }

  /**
   * Test email configuration
   *
   * @returns {Promise<boolean>} Test result
   */
  async testConnection() {
    try {
      if (!this.transporter) {
        await this.initialize();
      }

      await this.transporter.verify();
      logger.info('Email connection test successful');
      return true;
    } catch (error) {
      logger.error('Email connection test failed', {
        error: error.message,
      });
      return false;
    }
  }

  /**
   * Generate unique request ID
   *
   * @returns {string} Request ID
   */
  generateRequestId() {
    return `email-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Close transporter connection
   */
  async close() {
    if (this.transporter) {
      this.transporter.close();
      this.initialized = false;
      logger.info('Email service closed');
    }
  }
}

// Export singleton instance
const emailService = new EmailService();
export default emailService;
