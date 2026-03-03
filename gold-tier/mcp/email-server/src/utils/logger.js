/**
 * Logger Module
 *
 * Provides structured logging using Winston with file and console transports.
 *
 * @module logger
 */

import winston from 'winston';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync, mkdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Ensure logs directory exists
const logsDir = join(__dirname, '../../logs');
if (!existsSync(logsDir)) {
  mkdirSync(logsDir, { recursive: true });
}

/**
 * Custom log format
 */
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

/**
 * Console log format (human-readable)
 */
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let metaStr = '';
    if (Object.keys(meta).length > 0) {
      metaStr = '\n' + JSON.stringify(meta, null, 2);
    }
    return `${timestamp} [${level}]: ${message}${metaStr}`;
  })
);

/**
 * Create Winston logger instance
 */
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: {
    service: 'email-mcp-server',
    environment: process.env.NODE_ENV || 'development',
  },
  transports: [
    // File transport for all logs
    new winston.transports.File({
      filename: join(logsDir, 'email-server.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 5,
      tailable: true,
    }),
    // File transport for errors only
    new winston.transports.File({
      filename: join(logsDir, 'email-server-error.log'),
      level: 'error',
      maxsize: 10485760, // 10MB
      maxFiles: 5,
      tailable: true,
    }),
  ],
  // Handle uncaught exceptions
  exceptionHandlers: [
    new winston.transports.File({
      filename: join(logsDir, 'exceptions.log'),
    }),
  ],
  // Handle unhandled promise rejections
  rejectionHandlers: [
    new winston.transports.File({
      filename: join(logsDir, 'rejections.log'),
    }),
  ],
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production' || process.env.LOG_CONSOLE === 'true') {
  logger.add(
    new winston.transports.Console({
      format: consoleFormat,
    })
  );
}

/**
 * Log email operation
 *
 * @param {string} operation - Operation name
 * @param {Object} data - Operation data
 * @param {string} level - Log level (default: 'info')
 */
logger.logEmailOperation = function (operation, data, level = 'info') {
  this.log(level, `Email operation: ${operation}`, {
    operation,
    ...data,
  });
};

/**
 * Log MCP request
 *
 * @param {string} method - MCP method name
 * @param {Object} params - Request parameters
 */
logger.logMCPRequest = function (method, params) {
  this.info(`MCP request: ${method}`, {
    method,
    params: this.sanitizeParams(params),
  });
};

/**
 * Log MCP response
 *
 * @param {string} method - MCP method name
 * @param {Object} result - Response result
 * @param {number} duration - Request duration in ms
 */
logger.logMCPResponse = function (method, result, duration) {
  this.info(`MCP response: ${method}`, {
    method,
    success: result.success,
    duration: `${duration}ms`,
  });
};

/**
 * Sanitize parameters (remove sensitive data)
 *
 * @param {Object} params - Parameters to sanitize
 * @returns {Object} Sanitized parameters
 */
logger.sanitizeParams = function (params) {
  if (!params) return params;

  const sanitized = { ...params };

  // Remove sensitive fields
  const sensitiveFields = ['password', 'token', 'apiKey', 'secret'];
  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '***REDACTED***';
    }
  }

  // Truncate long body content
  if (sanitized.body && sanitized.body.length > 200) {
    sanitized.body = sanitized.body.substring(0, 200) + '... (truncated)';
  }

  return sanitized;
};

export default logger;
