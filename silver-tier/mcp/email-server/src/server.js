/**
 * MCP Email Server
 *
 * Model Context Protocol server for email functionality.
 * Provides tools for sending emails with comprehensive validation,
 * rate limiting, and logging.
 *
 * @module server
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import emailService from './services/emailService.js';
import validator from './utils/validator.js';
import rateLimiter from './utils/rateLimiter.js';
import logger from './utils/logger.js';
import config from './config/config.js';

/**
 * MCP Email Server class
 */
class MCPEmailServer {
  constructor() {
    this.server = new Server(
      {
        name: config.server.name,
        version: config.server.version,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.setupErrorHandlers();
  }

  /**
   * Setup MCP request handlers
   */
  setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      logger.info('Listing available tools');

      return {
        tools: [
          {
            name: 'send_email',
            description: 'Send an email using SMTP',
            inputSchema: {
              type: 'object',
              properties: {
                to: {
                  type: 'string',
                  description: 'Recipient email address',
                },
                subject: {
                  type: 'string',
                  description: 'Email subject',
                },
                body: {
                  type: 'string',
                  description: 'Email body (plain text or HTML)',
                },
                from: {
                  type: 'string',
                  description: 'Sender email address (optional)',
                },
                cc: {
                  type: ['string', 'array'],
                  description: 'CC recipients (optional)',
                },
                bcc: {
                  type: ['string', 'array'],
                  description: 'BCC recipients (optional)',
                },
              },
              required: ['to', 'subject', 'body'],
            },
          },
          {
            name: 'send_batch_emails',
            description: 'Send multiple emails in batch',
            inputSchema: {
              type: 'object',
              properties: {
                emails: {
                  type: 'array',
                  description: 'Array of email objects',
                  items: {
                    type: 'object',
                    properties: {
                      to: { type: 'string' },
                      subject: { type: 'string' },
                      body: { type: 'string' },
                      from: { type: 'string' },
                      cc: { type: ['string', 'array'] },
                      bcc: { type: ['string', 'array'] },
                    },
                    required: ['to', 'subject', 'body'],
                  },
                },
              },
              required: ['emails'],
            },
          },
          {
            name: 'test_email_connection',
            description: 'Test email server connection',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      const startTime = Date.now();

      logger.logMCPRequest(name, args);

      try {
        let result;

        switch (name) {
          case 'send_email':
            result = await this.handleSendEmail(args);
            break;

          case 'send_batch_emails':
            result = await this.handleSendBatchEmails(args);
            break;

          case 'test_email_connection':
            result = await this.handleTestConnection();
            break;

          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        const duration = Date.now() - startTime;
        logger.logMCPResponse(name, result, duration);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        const duration = Date.now() - startTime;

        logger.error('Tool execution failed', {
          tool: name,
          error: error.message,
          stack: error.stack,
          duration: `${duration}ms`,
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error: error.message,
                  tool: name,
                },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    });
  }

  /**
   * Handle send_email tool
   *
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result
   */
  async handleSendEmail(args) {
    // Check rate limit
    const rateLimitResult = rateLimiter.checkLimit('default');
    if (!rateLimitResult.allowed) {
      return {
        success: false,
        error: 'Rate limit exceeded',
        retryAfter: rateLimitResult.retryAfter,
        resetAt: new Date(rateLimitResult.resetAt).toISOString(),
      };
    }

    // Validate email data
    const validation = validator.validateEmail(args);
    if (!validation.valid) {
      return {
        success: false,
        error: 'Validation failed',
        validationErrors: validation.errors,
      };
    }

    // Send email
    const result = await emailService.sendEmail(validation.data);

    return {
      success: result.success,
      messageId: result.messageId,
      response: result.response,
      duration: result.duration,
      requestId: result.requestId,
      error: result.error,
      rateLimitRemaining: rateLimitResult.remaining,
    };
  }

  /**
   * Handle send_batch_emails tool
   *
   * @param {Object} args - Tool arguments
   * @returns {Promise<Object>} Result
   */
  async handleSendBatchEmails(args) {
    // Check rate limit (batch counts as multiple requests)
    const emailCount = args.emails?.length || 0;
    for (let i = 0; i < emailCount; i++) {
      const rateLimitResult = rateLimiter.checkLimit('default');
      if (!rateLimitResult.allowed) {
        return {
          success: false,
          error: 'Rate limit exceeded',
          retryAfter: rateLimitResult.retryAfter,
          resetAt: new Date(rateLimitResult.resetAt).toISOString(),
          processedCount: i,
        };
      }
    }

    // Validate batch data
    const validation = validator.validateBatch(args);
    if (!validation.valid) {
      return {
        success: false,
        error: 'Validation failed',
        validationErrors: validation.errors,
      };
    }

    // Send batch
    const result = await emailService.sendBatch(validation.data.emails);

    return {
      success: result.failure === 0,
      total: result.total,
      successCount: result.success,
      failureCount: result.failure,
      results: result.results,
    };
  }

  /**
   * Handle test_email_connection tool
   *
   * @returns {Promise<Object>} Result
   */
  async handleTestConnection() {
    const isConnected = await emailService.testConnection();

    return {
      success: isConnected,
      message: isConnected
        ? 'Email server connection successful'
        : 'Email server connection failed',
      config: {
        host: config.email.host,
        port: config.email.port,
        secure: config.email.secure,
        user: config.email.user,
      },
    };
  }

  /**
   * Setup error handlers
   */
  setupErrorHandlers() {
    this.server.onerror = (error) => {
      logger.error('MCP Server error', {
        error: error.message,
        stack: error.stack,
      });
    };

    process.on('SIGINT', async () => {
      logger.info('Received SIGINT, shutting down gracefully');
      await this.shutdown();
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      logger.info('Received SIGTERM, shutting down gracefully');
      await this.shutdown();
      process.exit(0);
    });
  }

  /**
   * Initialize and start the server
   */
  async start() {
    try {
      logger.info('Starting MCP Email Server', {
        name: config.server.name,
        version: config.server.version,
        environment: config.server.environment,
      });

      // Initialize email service
      await emailService.initialize();

      // Create transport
      const transport = new StdioServerTransport();

      // Connect server to transport
      await this.server.connect(transport);

      logger.info('MCP Email Server started successfully', {
        transport: 'stdio',
      });

      // Log configuration (sanitized)
      logger.info('Server configuration', {
        emailHost: config.email.host,
        emailPort: config.email.port,
        emailSecure: config.email.secure,
        maxEmailSize: config.security.maxEmailSize,
        maxRecipients: config.security.maxRecipients,
        rateLimitPerMinute: config.security.rateLimitPerMinute,
      });
    } catch (error) {
      logger.error('Failed to start MCP Email Server', {
        error: error.message,
        stack: error.stack,
      });
      process.exit(1);
    }
  }

  /**
   * Shutdown server gracefully
   */
  async shutdown() {
    logger.info('Shutting down MCP Email Server');

    try {
      // Close email service
      await emailService.close();

      // Stop rate limiter cleanup
      rateLimiter.stopCleanup();

      // Close server
      await this.server.close();

      logger.info('MCP Email Server shutdown complete');
    } catch (error) {
      logger.error('Error during shutdown', {
        error: error.message,
        stack: error.stack,
      });
    }
  }
}

// Create and start server
const server = new MCPEmailServer();
server.start().catch((error) => {
  logger.error('Fatal error starting server', {
    error: error.message,
    stack: error.stack,
  });
  process.exit(1);
});

export default server;
