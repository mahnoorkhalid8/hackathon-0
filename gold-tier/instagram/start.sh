#!/bin/bash
# Instagram Workflow - Quick Start Script
# Run this to start the complete system

echo "=========================================="
echo "Instagram Workflow System - Starting"
echo "=========================================="
echo ""

# Check if folders exist
if [ ! -d "workflow/Public" ]; then
    echo "Setting up folders..."
    python ig_workflow_manager.py --setup
    echo ""
fi

# Check credentials
if ! grep -q "INSTAGRAM_BUSINESS_ID" ../.env 2>/dev/null; then
    echo "ERROR: Instagram credentials not found in ../.env"
    echo "Please configure your credentials first"
    exit 1
fi

echo "✓ Credentials found"
echo "✓ Folders ready"
echo ""

# Start public server in background
echo "Starting public image server..."
python public_server.py &
SERVER_PID=$!
echo "✓ Server started (PID: $SERVER_PID)"
echo ""

# Wait for server to start
sleep 2

# Start workflow manager
echo "Starting workflow manager..."
echo "=========================================="
echo ""
python ig_workflow_manager.py

# Cleanup on exit
kill $SERVER_PID 2>/dev/null
