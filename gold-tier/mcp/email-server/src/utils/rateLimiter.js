/**
 * Rate Limiter Module
 *
 * Implements token bucket rate limiting to prevent abuse.
 *
 * @module rateLimiter
 */

import logger from './logger.js';
import config from '../config/config.js';

/**
 * Rate Limiter class using token bucket algorithm
 */
class RateLimiter {
  constructor() {
    this.buckets = new Map();
    this.maxTokens = config.security.rateLimitPerMinute;
    this.refillRate = this.maxTokens / 60; // Tokens per second
    this.cleanupInterval = null;

    // Start cleanup interval
    this.startCleanup();
  }

  /**
   * Check if request is allowed
   *
   * @param {string} identifier - Client identifier (IP, user ID, etc.)
   * @returns {Object} Rate limit result
   */
  checkLimit(identifier) {
    const now = Date.now();
    let bucket = this.buckets.get(identifier);

    if (!bucket) {
      // Create new bucket
      bucket = {
        tokens: this.maxTokens - 1,
        lastRefill: now,
      };
      this.buckets.set(identifier, bucket);

      return {
        allowed: true,
        remaining: bucket.tokens,
        resetAt: now + 60000,
      };
    }

    // Refill tokens based on time elapsed
    const timePassed = (now - bucket.lastRefill) / 1000; // seconds
    const tokensToAdd = timePassed * this.refillRate;
    bucket.tokens = Math.min(this.maxTokens, bucket.tokens + tokensToAdd);
    bucket.lastRefill = now;

    if (bucket.tokens >= 1) {
      // Allow request and consume token
      bucket.tokens -= 1;

      return {
        allowed: true,
        remaining: Math.floor(bucket.tokens),
        resetAt: now + 60000,
      };
    } else {
      // Rate limit exceeded
      logger.warn('Rate limit exceeded', {
        identifier,
        tokens: bucket.tokens,
      });

      return {
        allowed: false,
        remaining: 0,
        resetAt: now + Math.ceil((1 - bucket.tokens) / this.refillRate) * 1000,
        retryAfter: Math.ceil((1 - bucket.tokens) / this.refillRate),
      };
    }
  }

  /**
   * Reset rate limit for identifier
   *
   * @param {string} identifier - Client identifier
   */
  reset(identifier) {
    this.buckets.delete(identifier);
    logger.info('Rate limit reset', { identifier });
  }

  /**
   * Get current status for identifier
   *
   * @param {string} identifier - Client identifier
   * @returns {Object} Current status
   */
  getStatus(identifier) {
    const bucket = this.buckets.get(identifier);

    if (!bucket) {
      return {
        tokens: this.maxTokens,
        maxTokens: this.maxTokens,
      };
    }

    // Refill tokens
    const now = Date.now();
    const timePassed = (now - bucket.lastRefill) / 1000;
    const tokensToAdd = timePassed * this.refillRate;
    const currentTokens = Math.min(this.maxTokens, bucket.tokens + tokensToAdd);

    return {
      tokens: Math.floor(currentTokens),
      maxTokens: this.maxTokens,
    };
  }

  /**
   * Start cleanup interval to remove old buckets
   */
  startCleanup() {
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      const maxAge = 300000; // 5 minutes

      for (const [identifier, bucket] of this.buckets.entries()) {
        if (now - bucket.lastRefill > maxAge) {
          this.buckets.delete(identifier);
        }
      }

      if (this.buckets.size > 0) {
        logger.debug('Rate limiter cleanup', {
          bucketsRemaining: this.buckets.size,
        });
      }
    }, 60000); // Run every minute
  }

  /**
   * Stop cleanup interval
   */
  stopCleanup() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }

  /**
   * Clear all buckets
   */
  clear() {
    this.buckets.clear();
    logger.info('Rate limiter cleared');
  }
}

// Export singleton instance
const rateLimiter = new RateLimiter();
export default rateLimiter;
