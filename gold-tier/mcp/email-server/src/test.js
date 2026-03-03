/**
 * Test Suite for MCP Email Server
 *
 * Tests email service, validation, rate limiting, and MCP integration.
 *
 * @module test
 */

import emailService from './services/emailService.js';
import validator from './utils/validator.js';
import rateLimiter from './utils/rateLimiter.js';
import logger from './utils/logger.js';

/**
 * Test results tracker
 */
const results = {
  passed: 0,
  failed: 0,
  tests: [],
};

/**
 * Test helper function
 */
async function test(name, fn) {
  try {
    await fn();
    results.passed++;
    results.tests.push({ name, status: 'PASS' });
    console.log(`✓ ${name}`);
  } catch (error) {
    results.failed++;
    results.tests.push({ name, status: 'FAIL', error: error.message });
    console.log(`✗ ${name}`);
    console.log(`  Error: ${error.message}`);
  }
}

/**
 * Assert helper
 */
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

/**
 * Run all tests
 */
async function runTests() {
  console.log('='.repeat(70));
  console.log('  MCP Email Server - Test Suite');
  console.log('='.repeat(70));
  console.log();

  // ========================================================================
  // Validation Tests
  // ========================================================================

  console.log('[1] Validation Tests');
  console.log('-'.repeat(70));

  await test('Valid email passes validation', () => {
    const result = validator.validateEmail({
      to: 'test@example.com',
      subject: 'Test Subject',
      body: 'Test body content',
    });

    assert(result.valid === true, 'Should be valid');
    assert(result.errors.length === 0, 'Should have no errors');
    assert(result.data !== null, 'Should have data');
  });

  await test('Missing required fields fails validation', () => {
    const result = validator.validateEmail({
      to: 'test@example.com',
      // Missing subject and body
    });

    assert(result.valid === false, 'Should be invalid');
    assert(result.errors.length > 0, 'Should have errors');
  });

  await test('Invalid email address fails validation', () => {
    const result = validator.validateEmail({
      to: 'invalid-email',
      subject: 'Test',
      body: 'Test',
    });

    assert(result.valid === false, 'Should be invalid');
    assert(
      result.errors.some((e) => e.field === 'to'),
      'Should have error for "to" field'
    );
  });

  await test('Empty subject fails validation', () => {
    const result = validator.validateEmail({
      to: 'test@example.com',
      subject: '',
      body: 'Test',
    });

    assert(result.valid === false, 'Should be invalid');
  });

  await test('Subject exceeding max length fails validation', () => {
    const result = validator.validateEmail({
      to: 'test@example.com',
      subject: 'x'.repeat(1000),
      body: 'Test',
    });

    assert(result.valid === false, 'Should be invalid');
  });

  await test('Valid CC and BCC pass validation', () => {
    const result = validator.validateEmail({
      to: 'test@example.com',
      subject: 'Test',
      body: 'Test',
      cc: 'cc@example.com',
      bcc: ['bcc1@example.com', 'bcc2@example.com'],
    });

    assert(result.valid === true, 'Should be valid');
  });

  await test('Batch validation with valid emails passes', () => {
    const result = validator.validateBatch({
      emails: [
        {
          to: 'test1@example.com',
          subject: 'Test 1',
          body: 'Body 1',
        },
        {
          to: 'test2@example.com',
          subject: 'Test 2',
          body: 'Body 2',
        },
      ],
    });

    assert(result.valid === true, 'Should be valid');
    assert(result.data.emails.length === 2, 'Should have 2 emails');
  });

  await test('Batch validation with invalid email fails', () => {
    const result = validator.validateBatch({
      emails: [
        {
          to: 'test1@example.com',
          subject: 'Test 1',
          body: 'Body 1',
        },
        {
          to: 'invalid-email',
          subject: 'Test 2',
          body: 'Body 2',
        },
      ],
    });

    assert(result.valid === false, 'Should be invalid');
  });

  console.log();

  // ========================================================================
  // Rate Limiter Tests
  // ========================================================================

  console.log('[2] Rate Limiter Tests');
  console.log('-'.repeat(70));

  await test('First request is allowed', () => {
    rateLimiter.clear();
    const result = rateLimiter.checkLimit('test-user-1');

    assert(result.allowed === true, 'Should be allowed');
    assert(result.remaining >= 0, 'Should have remaining tokens');
  });

  await test('Multiple requests within limit are allowed', () => {
    rateLimiter.clear();

    for (let i = 0; i < 5; i++) {
      const result = rateLimiter.checkLimit('test-user-2');
      assert(result.allowed === true, `Request ${i + 1} should be allowed`);
    }
  });

  await test('Rate limit status returns correct info', () => {
    rateLimiter.clear();
    rateLimiter.checkLimit('test-user-3');

    const status = rateLimiter.getStatus('test-user-3');

    assert(status.tokens >= 0, 'Should have tokens');
    assert(status.maxTokens > 0, 'Should have max tokens');
  });

  await test('Rate limit reset clears bucket', () => {
    rateLimiter.clear();
    rateLimiter.checkLimit('test-user-4');
    rateLimiter.reset('test-user-4');

    const status = rateLimiter.getStatus('test-user-4');

    assert(
      status.tokens === status.maxTokens,
      'Should have full tokens after reset'
    );
  });

  console.log();

  // ========================================================================
  // Email Service Tests
  // ========================================================================

  console.log('[3] Email Service Tests');
  console.log('-'.repeat(70));

  await test('Email service initializes', async () => {
    // Note: This will fail if EMAIL_USER and EMAIL_PASSWORD are not set
    try {
      const initialized = await emailService.initialize();
      assert(initialized === true, 'Should initialize successfully');
    } catch (error) {
      // If initialization fails due to missing credentials, that's expected in test
      if (error.message.includes('Missing credentials')) {
        console.log('  (Skipped: Email credentials not configured)');
        return;
      }
      throw error;
    }
  });

  await test('Request ID generation is unique', () => {
    const id1 = emailService.generateRequestId();
    const id2 = emailService.generateRequestId();

    assert(id1 !== id2, 'Request IDs should be unique');
    assert(id1.startsWith('email-'), 'Should have correct prefix');
  });

  console.log();

  // ========================================================================
  // Integration Tests
  // ========================================================================

  console.log('[4] Integration Tests');
  console.log('-'.repeat(70));

  await test('Complete email workflow validation', () => {
    // Validate email
    const validation = validator.validateEmail({
      to: 'recipient@example.com',
      subject: 'Integration Test',
      body: 'This is a test email',
    });

    assert(validation.valid === true, 'Validation should pass');

    // Check rate limit
    const rateLimit = rateLimiter.checkLimit('integration-test');

    assert(rateLimit.allowed === true, 'Rate limit should allow');

    // Note: Actual sending would require valid SMTP credentials
  });

  console.log();

  // ========================================================================
  // Test Summary
  // ========================================================================

  console.log('='.repeat(70));
  console.log('  Test Summary');
  console.log('='.repeat(70));
  console.log();
  console.log(`Total Tests: ${results.passed + results.failed}`);
  console.log(`Passed: ${results.passed}`);
  console.log(`Failed: ${results.failed}`);
  console.log();

  if (results.failed === 0) {
    console.log('✓ All tests passed!');
    console.log();
    return 0;
  } else {
    console.log('✗ Some tests failed:');
    console.log();
    results.tests
      .filter((t) => t.status === 'FAIL')
      .forEach((t) => {
        console.log(`  - ${t.name}`);
        console.log(`    ${t.error}`);
      });
    console.log();
    return 1;
  }
}

// Run tests
runTests()
  .then((exitCode) => {
    process.exit(exitCode);
  })
  .catch((error) => {
    console.error('Test suite failed:', error);
    process.exit(1);
  });
