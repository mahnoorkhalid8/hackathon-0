/**
 * Configuration Module
 *
 * Loads and validates configuration from environment variables.
 *
 * @module config
 */

import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Configuration object
 */
const config = {
  // Server configuration
  server: {
    name: process.env.SERVER_NAME || 'silver-tier-email-server',
    version: process.env.SERVER_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  },

  // Email configuration
  email: {
    host: process.env.EMAIL_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.EMAIL_PORT || '587', 10),
    secure: process.env.EMAIL_SECURE === 'true', // true for 465, false for 587
    user: process.env.EMAIL_USER,
    password: process.env.EMAIL_PASSWORD,
    from: process.env.EMAIL_FROM || process.env.EMAIL_USER,
  },

  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || join(__dirname, '../../logs/email-server.log'),
    maxSize: process.env.LOG_MAX_SIZE || '10m',
    maxFiles: parseInt(process.env.LOG_MAX_FILES || '5', 10),
    console: process.env.LOG_CONSOLE !== 'false',
  },

  // Security configuration
  security: {
    maxEmailSize: parseInt(process.env.MAX_EMAIL_SIZE || '10485760', 10), // 10MB
    maxRecipients: parseInt(process.env.MAX_RECIPIENTS || '50', 10),
    allowedDomains: process.env.ALLOWED_DOMAINS
      ? process.env.ALLOWED_DOMAINS.split(',')
      : [],
    blockedDomains: process.env.BLOCKED_DOMAINS
      ? process.env.BLOCKED_DOMAINS.split(',')
      : [],
    rateLimitPerMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || '60', 10),
  },

  // MCP configuration
  mcp: {
    transport: process.env.MCP_TRANSPORT || 'stdio',
    port: parseInt(process.env.MCP_PORT || '3000', 10),
  },
};

/**
 * Validate required configuration
 */
function validateConfig() {
  const errors = [];

  // Validate email configuration
  if (!config.email.user) {
    errors.push('EMAIL_USER is required');
  }

  if (!config.email.password) {
    errors.push('EMAIL_PASSWORD is required');
  }

  if (!config.email.host) {
    errors.push('EMAIL_HOST is required');
  }

  if (isNaN(config.email.port) || config.email.port < 1 || config.email.port > 65535) {
    errors.push('EMAIL_PORT must be a valid port number (1-65535)');
  }

  // Validate security configuration
  if (config.security.maxEmailSize < 1024) {
    errors.push('MAX_EMAIL_SIZE must be at least 1024 bytes');
  }

  if (config.security.maxRecipients < 1) {
    errors.push('MAX_RECIPIENTS must be at least 1');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}

// Validate configuration on load
validateConfig();

export default config;
