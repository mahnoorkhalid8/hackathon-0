/**
 * Validation Module
 *
 * Validates email data using Joi schemas with comprehensive security checks.
 *
 * @module validator
 */

import Joi from 'joi';
import logger from './logger.js';
import config from '../config/config.js';

/**
 * Email validation schema
 */
const emailSchema = Joi.object({
  to: Joi.string()
    .email({ tlds: { allow: true } })
    .required()
    .messages({
      'string.email': 'Invalid recipient email address',
      'any.required': 'Recipient email address is required',
    }),

  subject: Joi.string()
    .min(1)
    .max(998) // RFC 2822 limit
    .required()
    .messages({
      'string.min': 'Subject cannot be empty',
      'string.max': 'Subject exceeds maximum length (998 characters)',
      'any.required': 'Subject is required',
    }),

  body: Joi.string()
    .min(1)
    .max(config.security.maxEmailSize)
    .required()
    .messages({
      'string.min': 'Email body cannot be empty',
      'string.max': `Email body exceeds maximum size (${config.security.maxEmailSize} bytes)`,
      'any.required': 'Email body is required',
    }),

  from: Joi.string()
    .email({ tlds: { allow: true } })
    .optional()
    .messages({
      'string.email': 'Invalid sender email address',
    }),

  cc: Joi.alternatives()
    .try(
      Joi.string().email({ tlds: { allow: true } }),
      Joi.array().items(Joi.string().email({ tlds: { allow: true } }))
    )
    .optional()
    .messages({
      'string.email': 'Invalid CC email address',
    }),

  bcc: Joi.alternatives()
    .try(
      Joi.string().email({ tlds: { allow: true } }),
      Joi.array().items(Joi.string().email({ tlds: { allow: true } }))
    )
    .optional()
    .messages({
      'string.email': 'Invalid BCC email address',
    }),

  attachments: Joi.array()
    .items(
      Joi.object({
        filename: Joi.string().required(),
        path: Joi.string().optional(),
        content: Joi.alternatives().try(Joi.string(), Joi.binary()).optional(),
        contentType: Joi.string().optional(),
      })
    )
    .optional(),
}).options({ stripUnknown: true });

/**
 * Batch email validation schema
 */
const batchEmailSchema = Joi.object({
  emails: Joi.array()
    .items(emailSchema)
    .min(1)
    .max(config.security.maxRecipients)
    .required()
    .messages({
      'array.min': 'At least one email is required',
      'array.max': `Batch size exceeds maximum (${config.security.maxRecipients})`,
      'any.required': 'Emails array is required',
    }),
}).options({ stripUnknown: true });

/**
 * Validator class
 */
class Validator {
  /**
   * Validate email data
   *
   * @param {Object} emailData - Email data to validate
   * @returns {Object} Validation result
   */
  validateEmail(emailData) {
    const { error, value } = emailSchema.validate(emailData, {
      abortEarly: false,
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      }));

      logger.warn('Email validation failed', {
        errors,
        to: emailData?.to,
      });

      return {
        valid: false,
        errors,
        data: null,
      };
    }

    // Additional security checks
    const securityCheck = this.performSecurityChecks(value);
    if (!securityCheck.valid) {
      return securityCheck;
    }

    return {
      valid: true,
      errors: [],
      data: value,
    };
  }

  /**
   * Validate batch email data
   *
   * @param {Object} batchData - Batch email data to validate
   * @returns {Object} Validation result
   */
  validateBatch(batchData) {
    const { error, value } = batchEmailSchema.validate(batchData, {
      abortEarly: false,
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      }));

      logger.warn('Batch email validation failed', {
        errors,
        count: batchData?.emails?.length,
      });

      return {
        valid: false,
        errors,
        data: null,
      };
    }

    // Validate each email individually
    const emailResults = [];
    for (let i = 0; i < value.emails.length; i++) {
      const result = this.validateEmail(value.emails[i]);
      if (!result.valid) {
        return {
          valid: false,
          errors: [
            {
              field: `emails[${i}]`,
              message: `Email ${i + 1} validation failed`,
              details: result.errors,
            },
          ],
          data: null,
        };
      }
      emailResults.push(result.data);
    }

    return {
      valid: true,
      errors: [],
      data: { emails: emailResults },
    };
  }

  /**
   * Perform security checks on email data
   *
   * @param {Object} emailData - Validated email data
   * @returns {Object} Security check result
   */
  performSecurityChecks(emailData) {
    const errors = [];

    // Check recipient count
    const recipientCount = this.countRecipients(emailData);
    if (recipientCount > config.security.maxRecipients) {
      errors.push({
        field: 'recipients',
        message: `Total recipients (${recipientCount}) exceeds maximum (${config.security.maxRecipients})`,
      });
    }

    // Check allowed domains
    if (config.security.allowedDomains.length > 0) {
      const domain = this.extractDomain(emailData.to);
      if (!config.security.allowedDomains.includes(domain)) {
        errors.push({
          field: 'to',
          message: `Domain ${domain} is not in allowed domains list`,
        });
      }
    }

    // Check blocked domains
    if (config.security.blockedDomains.length > 0) {
      const domain = this.extractDomain(emailData.to);
      if (config.security.blockedDomains.includes(domain)) {
        errors.push({
          field: 'to',
          message: `Domain ${domain} is blocked`,
        });
      }
    }

    // Check for suspicious content
    const suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /onerror=/i,
      /onclick=/i,
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(emailData.body)) {
        errors.push({
          field: 'body',
          message: 'Email body contains potentially malicious content',
        });
        break;
      }
    }

    if (errors.length > 0) {
      logger.warn('Email security check failed', {
        errors,
        to: emailData.to,
      });

      return {
        valid: false,
        errors,
        data: null,
      };
    }

    return {
      valid: true,
      errors: [],
      data: emailData,
    };
  }

  /**
   * Count total recipients (to + cc + bcc)
   *
   * @param {Object} emailData - Email data
   * @returns {number} Total recipient count
   */
  countRecipients(emailData) {
    let count = 1; // 'to' field

    if (emailData.cc) {
      count += Array.isArray(emailData.cc) ? emailData.cc.length : 1;
    }

    if (emailData.bcc) {
      count += Array.isArray(emailData.bcc) ? emailData.bcc.length : 1;
    }

    return count;
  }

  /**
   * Extract domain from email address
   *
   * @param {string} email - Email address
   * @returns {string} Domain
   */
  extractDomain(email) {
    return email.split('@')[1]?.toLowerCase() || '';
  }
}

// Export singleton instance
const validator = new Validator();
export default validator;
