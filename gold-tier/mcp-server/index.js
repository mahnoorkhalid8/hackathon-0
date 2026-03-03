/**
 * Digital FTE MCP Server
 *
 * A Model Context Protocol server that provides secure local file operations
 * for the Digital FTE system. Allows Claude Code to read, write, and move
 * markdown files within the AI_Employee_Vault directory.
 *
 * Security:
 * - All operations are restricted to the vault directory
 * - Path traversal attacks are prevented
 * - Only markdown files can be manipulated
 * - No network operations allowed
 *
 * @requires Node.js v24+
 * @requires @modelcontextprotocol/sdk
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current directory (ESM equivalent of __dirname)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const VAULT_ROOT = path.resolve(__dirname, '..', 'AI_Employee_Vault');
const ALLOWED_EXTENSIONS = ['.md', '.markdown'];

/**
 * Security: Validate and normalize file paths
 * Prevents directory traversal attacks and ensures operations stay within vault
 *
 * @param {string} filePath - The file path to validate
 * @returns {string} Normalized absolute path
 * @throws {Error} If path is outside vault or invalid
 */
function validatePath(filePath) {
  // Resolve to absolute path
  const absolutePath = path.resolve(VAULT_ROOT, filePath);

  // Ensure path is within vault directory
  if (!absolutePath.startsWith(VAULT_ROOT)) {
    throw new Error(`Access denied: Path must be within AI_Employee_Vault`);
  }

  // Check file extension for write/move operations
  const ext = path.extname(absolutePath).toLowerCase();
  if (ext && !ALLOWED_EXTENSIONS.includes(ext)) {
    throw new Error(`Invalid file type: Only markdown files (.md) are allowed`);
  }

  return absolutePath;
}

/**
 * Security: Validate folder path
 * Ensures folder operations stay within allowed directories
 *
 * @param {string} folderPath - The folder path to validate
 * @returns {string} Normalized absolute path
 * @throws {Error} If path is outside vault
 */
function validateFolderPath(folderPath) {
  const absolutePath = path.resolve(VAULT_ROOT, folderPath);

  if (!absolutePath.startsWith(VAULT_ROOT)) {
    throw new Error(`Access denied: Path must be within AI_Employee_Vault`);
  }

  return absolutePath;
}

/**
 * Tool: Read Markdown File
 * Reads the contents of a markdown file from the vault
 *
 * @param {string} filePath - Relative path from vault root
 * @returns {Promise<string>} File contents
 */
async function readMarkdownFile(filePath) {
  try {
    const absolutePath = validatePath(filePath);

    // Check if file exists
    try {
      await fs.access(absolutePath);
    } catch {
      throw new Error(`File not found: ${filePath}`);
    }

    // Read file contents
    const content = await fs.readFile(absolutePath, 'utf-8');

    return {
      success: true,
      path: filePath,
      content: content,
      size: content.length,
      message: `Successfully read ${filePath}`
    };
  } catch (error) {
    return {
      success: false,
      path: filePath,
      error: error.message
    };
  }
}

/**
 * Tool: Write Markdown File
 * Writes content to a markdown file in the vault
 * Creates parent directories if they don't exist
 *
 * @param {string} filePath - Relative path from vault root
 * @param {string} content - Content to write
 * @param {boolean} overwrite - Whether to overwrite existing file (default: false)
 * @returns {Promise<Object>} Operation result
 */
async function writeMarkdownFile(filePath, content, overwrite = false) {
  try {
    const absolutePath = validatePath(filePath);

    // Check if file exists
    let fileExists = false;
    try {
      await fs.access(absolutePath);
      fileExists = true;
    } catch {
      // File doesn't exist, which is fine
    }

    // Prevent accidental overwrites
    if (fileExists && !overwrite) {
      throw new Error(
        `File already exists: ${filePath}. Set overwrite=true to replace it.`
      );
    }

    // Ensure parent directory exists
    const directory = path.dirname(absolutePath);
    await fs.mkdir(directory, { recursive: true });

    // Write file
    await fs.writeFile(absolutePath, content, 'utf-8');

    return {
      success: true,
      path: filePath,
      size: content.length,
      overwritten: fileExists,
      message: fileExists
        ? `Successfully overwrote ${filePath}`
        : `Successfully created ${filePath}`
    };
  } catch (error) {
    return {
      success: false,
      path: filePath,
      error: error.message
    };
  }
}

/**
 * Tool: Move File
 * Moves a file from one location to another within the vault
 * Supports moving between folders (Inbox, Needs_Action, Done)
 *
 * @param {string} sourcePath - Source file path (relative to vault)
 * @param {string} destinationPath - Destination path (relative to vault)
 * @param {boolean} overwrite - Whether to overwrite destination if exists
 * @returns {Promise<Object>} Operation result
 */
async function moveFile(sourcePath, destinationPath, overwrite = false) {
  try {
    const absoluteSource = validatePath(sourcePath);
    const absoluteDestination = validatePath(destinationPath);

    // Check if source exists
    try {
      await fs.access(absoluteSource);
    } catch {
      throw new Error(`Source file not found: ${sourcePath}`);
    }

    // Check if destination exists
    let destExists = false;
    try {
      await fs.access(absoluteDestination);
      destExists = true;
    } catch {
      // Destination doesn't exist, which is fine
    }

    if (destExists && !overwrite) {
      throw new Error(
        `Destination already exists: ${destinationPath}. Set overwrite=true to replace it.`
      );
    }

    // Ensure destination directory exists
    const destDirectory = path.dirname(absoluteDestination);
    await fs.mkdir(destDirectory, { recursive: true });

    // Read source content
    const content = await fs.readFile(absoluteSource, 'utf-8');

    // Write to destination
    await fs.writeFile(absoluteDestination, content, 'utf-8');

    // Verify write was successful
    const verifyContent = await fs.readFile(absoluteDestination, 'utf-8');
    if (verifyContent !== content) {
      throw new Error('Content verification failed after move');
    }

    // Delete source file
    await fs.unlink(absoluteSource);

    // Verify source was deleted
    try {
      await fs.access(absoluteSource);
      throw new Error('Source file still exists after deletion');
    } catch {
      // Good - source file is gone
    }

    return {
      success: true,
      source: sourcePath,
      destination: destinationPath,
      size: content.length,
      overwritten: destExists,
      message: `Successfully moved ${sourcePath} to ${destinationPath}`
    };
  } catch (error) {
    return {
      success: false,
      source: sourcePath,
      destination: destinationPath,
      error: error.message
    };
  }
}

/**
 * Tool: List Files
 * Lists markdown files in a specific folder
 *
 * @param {string} folderPath - Folder path relative to vault root
 * @returns {Promise<Object>} List of files
 */
async function listFiles(folderPath) {
  try {
    const absolutePath = validateFolderPath(folderPath);

    // Check if directory exists
    try {
      await fs.access(absolutePath);
    } catch {
      throw new Error(`Directory not found: ${folderPath}`);
    }

    // Read directory contents
    const entries = await fs.readdir(absolutePath, { withFileTypes: true });

    // Filter for markdown files
    const files = entries
      .filter(entry => {
        if (!entry.isFile()) return false;
        const ext = path.extname(entry.name).toLowerCase();
        return ALLOWED_EXTENSIONS.includes(ext);
      })
      .map(entry => entry.name);

    return {
      success: true,
      path: folderPath,
      files: files,
      count: files.length,
      message: `Found ${files.length} markdown file(s) in ${folderPath}`
    };
  } catch (error) {
    return {
      success: false,
      path: folderPath,
      error: error.message
    };
  }
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  // Create MCP server instance
  const server = new Server(
    {
      name: 'digital-fte-mcp-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  /**
   * Handler: List available tools
   * Returns the list of tools this server provides
   */
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: 'read_markdown',
          description: 'Read the contents of a markdown file from the AI_Employee_Vault',
          inputSchema: {
            type: 'object',
            properties: {
              file_path: {
                type: 'string',
                description: 'Path to the markdown file relative to AI_Employee_Vault (e.g., "Inbox/task.md")',
              },
            },
            required: ['file_path'],
          },
        },
        {
          name: 'write_markdown',
          description: 'Write content to a markdown file in the AI_Employee_Vault',
          inputSchema: {
            type: 'object',
            properties: {
              file_path: {
                type: 'string',
                description: 'Path to the markdown file relative to AI_Employee_Vault',
              },
              content: {
                type: 'string',
                description: 'Content to write to the file',
              },
              overwrite: {
                type: 'boolean',
                description: 'Whether to overwrite if file exists (default: false)',
                default: false,
              },
            },
            required: ['file_path', 'content'],
          },
        },
        {
          name: 'move_file',
          description: 'Move a file from one location to another within AI_Employee_Vault',
          inputSchema: {
            type: 'object',
            properties: {
              source_path: {
                type: 'string',
                description: 'Source file path relative to AI_Employee_Vault',
              },
              destination_path: {
                type: 'string',
                description: 'Destination file path relative to AI_Employee_Vault',
              },
              overwrite: {
                type: 'boolean',
                description: 'Whether to overwrite destination if exists (default: false)',
                default: false,
              },
            },
            required: ['source_path', 'destination_path'],
          },
        },
        {
          name: 'list_files',
          description: 'List markdown files in a folder within AI_Employee_Vault',
          inputSchema: {
            type: 'object',
            properties: {
              folder_path: {
                type: 'string',
                description: 'Folder path relative to AI_Employee_Vault (e.g., "Inbox", "Done")',
              },
            },
            required: ['folder_path'],
          },
        },
      ],
    };
  });

  /**
   * Handler: Execute tool
   * Routes tool calls to the appropriate handler function
   */
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'read_markdown': {
          const result = await readMarkdownFile(args.file_path);
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case 'write_markdown': {
          const result = await writeMarkdownFile(
            args.file_path,
            args.content,
            args.overwrite || false
          );
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case 'move_file': {
          const result = await moveFile(
            args.source_path,
            args.destination_path,
            args.overwrite || false
          );
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case 'list_files': {
          const result = await listFiles(args.folder_path);
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: error.message,
            }, null, 2),
          },
        ],
        isError: true,
      };
    }
  });

  // Start server with stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Digital FTE MCP Server running on stdio');
  console.error(`Vault root: ${VAULT_ROOT}`);
  console.error('Available tools: read_markdown, write_markdown, move_file, list_files');
}

// Start the server
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
