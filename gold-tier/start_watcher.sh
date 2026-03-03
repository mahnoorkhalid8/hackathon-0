#!/bin/bash
# Digital FTE Inbox Watcher - Startup Script
# Usage: ./start_watcher.sh

set -e

echo "=========================================="
echo "Digital FTE Inbox Watcher - Startup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check Claude CLI
echo "Checking Claude Code CLI..."
if ! command -v claude &> /dev/null; then
    echo "✗ Claude Code CLI not found"
    echo "  Please install Claude Code CLI first"
    exit 1
fi
claude_version=$(claude --version 2>&1)
echo "✓ $claude_version"
echo ""

# Verify directory structure
echo "Verifying directory structure..."
required_dirs=("AI_Employee_Vault" "AI_Employee_Vault/Inbox" "AI_Employee_Vault/Needs_Action" "AI_Employee_Vault/Done")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "✗ Required directory not found: $dir"
        exit 1
    fi
done
echo "✓ All required directories exist"
echo ""

# Check Dashboard
if [ ! -f "AI_Employee_Vault/Dashboard.md" ]; then
    echo "✗ Dashboard.md not found"
    exit 1
fi
echo "✓ Dashboard.md found"
echo ""

# Start the watcher
echo "=========================================="
echo "Starting Inbox Watcher..."
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 inbox_watcher.py
