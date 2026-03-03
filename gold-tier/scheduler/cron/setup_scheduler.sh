#!/bin/bash
#
# Silver Tier Digital FTE - Cron Scheduler Setup (Linux/Unix)
#
# This script sets up cron jobs for the Digital FTE system.
#
# Usage:
#   chmod +x setup_scheduler.sh
#   ./setup_scheduler.sh
#
# Author: Digital FTE System
# Date: 2026-02-13

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  Silver Tier Digital FTE - Scheduler Setup (Linux)${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Get current directory
PROJECT_DIR=$(pwd)
echo -e "${YELLOW}Project Directory: ${PROJECT_DIR}${NC}"
echo ""

# Check if Python is installed
echo -e "${GREEN}[1/6] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  Found: ${PYTHON_VERSION}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "  Found: ${PYTHON_VERSION}"
    PYTHON_CMD="python"
else
    echo -e "${RED}  ERROR: Python not found. Please install Python 3.13+${NC}"
    exit 1
fi

# Check if run_agent.py exists
echo -e "${GREEN}[2/6] Checking run_agent.py...${NC}"
if [ -f "run_agent.py" ]; then
    echo "  Found: run_agent.py"
else
    echo -e "${RED}  ERROR: run_agent.py not found in current directory${NC}"
    exit 1
fi

# Create logs directory
echo -e "${GREEN}[3/6] Creating logs directory...${NC}"
mkdir -p logs
echo "  Created: logs/"

# Update crontab template with current directory
echo -e "${GREEN}[4/6] Preparing crontab entries...${NC}"

CRON_FILE="scheduler/cron/crontab.txt"
TEMP_CRON="/tmp/digitalfte_cron_temp.txt"

if [ -f "$CRON_FILE" ]; then
    # Replace placeholder paths with actual paths
    sed "s|\$PROJECT_DIR|${PROJECT_DIR}|g" "$CRON_FILE" | \
    sed "s|\$PYTHON|${PYTHON_CMD}|g" > "$TEMP_CRON"
    echo "  Prepared crontab entries"
else
    echo -e "${RED}  ERROR: $CRON_FILE not found${NC}"
    exit 1
fi

# Show crontab entries
echo ""
echo -e "${YELLOW}Crontab entries to be added:${NC}"
echo "-----------------------------------------------------------"
grep -v "^#" "$TEMP_CRON" | grep -v "^$" || echo "(No entries found)"
echo "-----------------------------------------------------------"
echo ""

# Ask for confirmation
read -p "Install these cron jobs? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installation cancelled${NC}"
    rm -f "$TEMP_CRON"
    exit 0
fi

# Backup existing crontab
echo -e "${GREEN}[5/6] Backing up existing crontab...${NC}"
if crontab -l &> /dev/null; then
    crontab -l > "scheduler/cron/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    echo "  Backup created: scheduler/cron/crontab_backup_*.txt"
else
    echo "  No existing crontab to backup"
fi

# Install crontab
echo -e "${GREEN}[6/6] Installing crontab...${NC}"

# Get existing crontab (if any)
EXISTING_CRON=$(crontab -l 2>/dev/null || echo "")

# Remove old Digital FTE entries
FILTERED_CRON=$(echo "$EXISTING_CRON" | grep -v "Digital FTE" || true)

# Combine with new entries
{
    echo "$FILTERED_CRON"
    echo ""
    echo "# ============================================================================"
    echo "# Silver Tier Digital FTE - Scheduled Tasks"
    echo "# Installed: $(date)"
    echo "# ============================================================================"
    echo ""
    grep -v "^#" "$TEMP_CRON" | grep -v "^$"
} | crontab -

echo "  Crontab installed successfully"

# Cleanup
rm -f "$TEMP_CRON"

# Verify installation
echo ""
echo -e "${GREEN}Verifying installation...${NC}"
INSTALLED_JOBS=$(crontab -l | grep -c "run_agent.py" || echo "0")
echo "  Found $INSTALLED_JOBS Digital FTE cron job(s)"

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  Setup Complete!${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""
echo -e "${YELLOW}Scheduled tasks:${NC}"
echo "  - Watchers: Every 5 minutes"
echo "  - CEO Report: Monday 9:00 AM"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Verify cron jobs: crontab -l"
echo "  2. Check logs: tail -f logs/cron_watchers.log"
echo "  3. Test manually: python run_agent.py watchers"
echo ""
echo -e "${YELLOW}To view cron logs:${NC}"
echo "  tail -f logs/cron_watchers.log"
echo "  tail -f logs/cron_ceo_report.log"
echo ""
echo -e "${YELLOW}To uninstall:${NC}"
echo "  crontab -e  # Remove Digital FTE entries manually"
echo "  # Or restore backup:"
echo "  crontab scheduler/cron/crontab_backup_*.txt"
echo ""
echo -e "${YELLOW}To check cron service status:${NC}"
echo "  sudo systemctl status cron     # Debian/Ubuntu"
echo "  sudo systemctl status crond    # CentOS/RHEL"
echo ""
