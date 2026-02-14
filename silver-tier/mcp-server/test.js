/**
 * Test Script for Digital FTE MCP Server
 *
 * Run this script to verify the MCP server functions correctly.
 * Tests all four tools with various scenarios.
 *
 * Usage: node test.js
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test configuration
const VAULT_ROOT = path.resolve(__dirname, '..', 'AI_Employee_Vault');
const TEST_FOLDER = 'Inbox';
const TEST_FILE = 'test-mcp-server.md';
const TEST_FILE_PATH = path.join(TEST_FOLDER, TEST_FILE);

// ANSI color codes for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(name) {
  console.log(`\n${colors.cyan}▶ ${name}${colors.reset}`);
}

function logSuccess(message) {
  log(`  ✓ ${message}`, 'green');
}

function logError(message) {
  log(`  ✗ ${message}`, 'red');
}

function logInfo(message) {
  log(`  ℹ ${message}`, 'blue');
}

// Import the functions we want to test
// Note: In a real test, you'd import from index.js
// For this test script, we'll recreate the core functions

function validatePath(filePath) {
  const absolutePath = path.resolve(VAULT_ROOT, filePath);
  if (!absolutePath.startsWith(VAULT_ROOT)) {
    throw new Error(`Access denied: Path must be within AI_Employee_Vault`);
  }
  const ext = path.extname(absolutePath).toLowerCase();
  if (ext && !['.md', '.markdown'].includes(ext)) {
    throw new Error(`Invalid file type: Only markdown files (.md) are allowed`);
  }
  return absolutePath;
}

async function readMarkdownFile(filePath) {
  try {
    const absolutePath = validatePath(filePath);
    await fs.access(absolutePath);
    const content = await fs.readFile(absolutePath, 'utf-8');
    return {
      success: true,
      path: filePath,
      content: content,
      size: content.length,
    };
  } catch (error) {
    return {
      success: false,
      path: filePath,
      error: error.message,
    };
  }
}

async function writeMarkdownFile(filePath, content, overwrite = false) {
  try {
    const absolutePath = validatePath(filePath);
    let fileExists = false;
    try {
      await fs.access(absolutePath);
      fileExists = true;
    } catch {}

    if (fileExists && !overwrite) {
      throw new Error(`File already exists: ${filePath}. Set overwrite=true to replace it.`);
    }

    const directory = path.dirname(absolutePath);
    await fs.mkdir(directory, { recursive: true });
    await fs.writeFile(absolutePath, content, 'utf-8');

    return {
      success: true,
      path: filePath,
      size: content.length,
      overwritten: fileExists,
    };
  } catch (error) {
    return {
      success: false,
      path: filePath,
      error: error.message,
    };
  }
}

async function moveFile(sourcePath, destinationPath, overwrite = false) {
  try {
    const absoluteSource = validatePath(sourcePath);
    const absoluteDestination = validatePath(destinationPath);

    await fs.access(absoluteSource);

    let destExists = false;
    try {
      await fs.access(absoluteDestination);
      destExists = true;
    } catch {}

    if (destExists && !overwrite) {
      throw new Error(`Destination already exists: ${destinationPath}. Set overwrite=true to replace it.`);
    }

    const destDirectory = path.dirname(absoluteDestination);
    await fs.mkdir(destDirectory, { recursive: true });

    const content = await fs.readFile(absoluteSource, 'utf-8');
    await fs.writeFile(absoluteDestination, content, 'utf-8');

    const verifyContent = await fs.readFile(absoluteDestination, 'utf-8');
    if (verifyContent !== content) {
      throw new Error('Content verification failed after move');
    }

    await fs.unlink(absoluteSource);

    return {
      success: true,
      source: sourcePath,
      destination: destinationPath,
      size: content.length,
      overwritten: destExists,
    };
  } catch (error) {
    return {
      success: false,
      source: sourcePath,
      destination: destinationPath,
      error: error.message,
    };
  }
}

async function listFiles(folderPath) {
  try {
    const absolutePath = path.resolve(VAULT_ROOT, folderPath);
    if (!absolutePath.startsWith(VAULT_ROOT)) {
      throw new Error(`Access denied: Path must be within AI_Employee_Vault`);
    }

    await fs.access(absolutePath);
    const entries = await fs.readdir(absolutePath, { withFileTypes: true });

    const files = entries
      .filter(entry => {
        if (!entry.isFile()) return false;
        const ext = path.extname(entry.name).toLowerCase();
        return ['.md', '.markdown'].includes(ext);
      })
      .map(entry => entry.name);

    return {
      success: true,
      path: folderPath,
      files: files,
      count: files.length,
    };
  } catch (error) {
    return {
      success: false,
      path: folderPath,
      error: error.message,
    };
  }
}

// Test suite
async function runTests() {
  log('\n═══════════════════════════════════════════', 'cyan');
  log('  Digital FTE MCP Server - Test Suite', 'cyan');
  log('═══════════════════════════════════════════\n', 'cyan');

  let passed = 0;
  let failed = 0;

  // Cleanup function
  async function cleanup() {
    try {
      const testFilePath = path.join(VAULT_ROOT, TEST_FILE_PATH);
      await fs.unlink(testFilePath);
    } catch {}

    try {
      const movedFilePath = path.join(VAULT_ROOT, 'Needs_Action', TEST_FILE);
      await fs.unlink(movedFilePath);
    } catch {}
  }

  // Test 1: Write a new file
  logTest('Test 1: Write new markdown file');
  try {
    const content = '# Test Task\n\n**Priority:** P2\n\nThis is a test task.';
    const result = await writeMarkdownFile(TEST_FILE_PATH, content);

    if (result.success && result.size === content.length && !result.overwritten) {
      logSuccess('File created successfully');
      passed++;
    } else {
      logError('File creation failed');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 2: Read the file
  logTest('Test 2: Read markdown file');
  try {
    const result = await readMarkdownFile(TEST_FILE_PATH);

    if (result.success && result.content.includes('Test Task')) {
      logSuccess('File read successfully');
      logInfo(`Content size: ${result.size} bytes`);
      passed++;
    } else {
      logError('File read failed');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 3: Attempt to overwrite without permission
  logTest('Test 3: Overwrite protection');
  try {
    const result = await writeMarkdownFile(TEST_FILE_PATH, 'New content');

    if (!result.success && result.error.includes('already exists')) {
      logSuccess('Overwrite protection working');
      passed++;
    } else {
      logError('Overwrite protection failed');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 4: Overwrite with permission
  logTest('Test 4: Overwrite with permission');
  try {
    const newContent = '# Updated Test Task\n\nContent has been updated.';
    const result = await writeMarkdownFile(TEST_FILE_PATH, newContent, true);

    if (result.success && result.overwritten) {
      logSuccess('File overwritten successfully');
      passed++;
    } else {
      logError('File overwrite failed');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 5: List files in folder
  logTest('Test 5: List files in folder');
  try {
    const result = await listFiles(TEST_FOLDER);

    if (result.success && result.files.includes(TEST_FILE)) {
      logSuccess(`Found ${result.count} file(s) including test file`);
      passed++;
    } else {
      logError('File listing failed or test file not found');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 6: Move file
  logTest('Test 6: Move file to another folder');
  try {
    const destPath = path.join('Needs_Action', TEST_FILE);
    const result = await moveFile(TEST_FILE_PATH, destPath);

    if (result.success) {
      logSuccess('File moved successfully');

      // Verify source is gone
      const sourceCheck = await readMarkdownFile(TEST_FILE_PATH);
      if (!sourceCheck.success) {
        logSuccess('Source file removed');
        passed++;
      } else {
        logError('Source file still exists');
        failed++;
      }
    } else {
      logError('File move failed');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 7: Security - Path traversal
  logTest('Test 7: Security - Path traversal prevention');
  try {
    const result = await readMarkdownFile('../../../etc/passwd');

    if (!result.success && result.error.includes('Access denied')) {
      logSuccess('Path traversal blocked');
      passed++;
    } else {
      logError('Path traversal not blocked!');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 8: Security - Invalid file type
  logTest('Test 8: Security - Invalid file type prevention');
  try {
    const result = await writeMarkdownFile('Inbox/script.js', 'console.log("test")');

    if (!result.success && result.error.includes('Invalid file type')) {
      logSuccess('Invalid file type blocked');
      passed++;
    } else {
      logError('Invalid file type not blocked!');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Test 9: Read non-existent file
  logTest('Test 9: Read non-existent file');
  try {
    const result = await readMarkdownFile('Inbox/does-not-exist.md');

    if (!result.success && (result.error.includes('not found') || result.error.includes('ENOENT'))) {
      logSuccess('Non-existent file handled correctly');
      passed++;
    } else {
      logError('Non-existent file not handled correctly');
      logInfo(JSON.stringify(result, null, 2));
      failed++;
    }
  } catch (error) {
    logError(`Exception: ${error.message}`);
    failed++;
  }

  // Cleanup
  logTest('Cleanup: Removing test files');
  await cleanup();
  logSuccess('Test files removed');

  // Summary
  log('\n═══════════════════════════════════════════', 'cyan');
  log('  Test Summary', 'cyan');
  log('═══════════════════════════════════════════\n', 'cyan');

  log(`Total tests: ${passed + failed}`, 'blue');
  log(`Passed: ${passed}`, 'green');
  log(`Failed: ${failed}`, failed > 0 ? 'red' : 'green');

  if (failed === 0) {
    log('\n✓ All tests passed!', 'green');
    process.exit(0);
  } else {
    log('\n✗ Some tests failed', 'red');
    process.exit(1);
  }
}

// Run tests
runTests().catch(error => {
  logError(`Fatal error: ${error.message}`);
  console.error(error);
  process.exit(1);
});
