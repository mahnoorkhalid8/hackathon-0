# Silver Tier Digital FTE - Scheduler System

Complete scheduling solution for automated task execution with support for Windows Task Scheduler and Linux cron.

## Overview

The scheduler system automates the execution of Digital FTE tasks:
- **Watchers**: Run every 5 minutes to check for new emails and files
- **CEO Report**: Generate and send weekly report every Monday at 9:00 AM
- **Custom Tasks**: Execute specific task files on demand

## Components

```
scheduler/
├── windows/
│   ├── run_watchers.xml          # Task: Run watchers every 5 min
│   ├── ceo_report.xml            # Task: CEO report Monday 9 AM
│   └── setup_scheduler.ps1       # Windows setup script
├── cron/
│   ├── crontab.txt               # Cron job definitions
│   └── setup_scheduler.sh        # Linux setup script
└── README.md                     # This file

run_agent.py                      # Main orchestration script
```

## Quick Start

### Windows

```powershell
# Run as Administrator
cd C:\path\to\silver-tier
powershell -ExecutionPolicy Bypass -File scheduler\windows\setup_scheduler.ps1
```

### Linux/macOS

```bash
cd /path/to/silver-tier
chmod +x scheduler/cron/setup_scheduler.sh
./scheduler/cron/setup_scheduler.sh
```

## run_agent.py - Orchestration Script

### Commands

```bash
# Run all watchers (file + Gmail)
python run_agent.py watchers

# Run file watcher only
python run_agent.py file-watcher

# Run Gmail watcher only
python run_agent.py gmail-watcher

# Generate CEO report
python run_agent.py ceo-report

# Process specific task file
python run_agent.py task --file memory/Inbox/task.md

# Set log level
python run_agent.py watchers --log-level DEBUG
```

### Features

- ✅ Orchestrates all Digital FTE components
- ✅ Comprehensive logging to `logs/run_agent_*.log`
- ✅ Error handling and recovery
- ✅ Execution time tracking
- ✅ JSON result output
- ✅ Exit codes (0=success, 1=failure)

## Windows Task Scheduler Setup

### Automatic Setup

```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File scheduler\windows\setup_scheduler.ps1
```

This will:
1. Check Python installation
2. Update XML files with current directory
3. Create `\DigitalFTE` folder in Task Scheduler
4. Import scheduled tasks
5. Verify installation

### Manual Setup

1. Open Task Scheduler (`taskschd.msc`)
2. Right-click "Task Scheduler Library" → "Import Task"
3. Select `scheduler\windows\run_watchers.xml`
4. Edit "Actions" tab to update paths if needed
5. Repeat for `ceo_report.xml`

### Scheduled Tasks

**RunWatchers**
- **Schedule**: Every 5 minutes
- **Command**: `python run_agent.py watchers`
- **Timeout**: 10 minutes
- **Network**: Required
- **Wake**: No

**CEOReport**
- **Schedule**: Monday 9:00 AM
- **Command**: `python run_agent.py ceo-report`
- **Timeout**: 30 minutes
- **Network**: Required
- **Wake**: Yes

### Verification

```powershell
# List tasks
Get-ScheduledTask -TaskPath "\DigitalFTE\*"

# View task details
Get-ScheduledTask -TaskName "DigitalFTE\RunWatchers" | Get-ScheduledTaskInfo

# Run task manually
Start-ScheduledTask -TaskName "DigitalFTE\RunWatchers"

# View task history
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | Where-Object {$_.Message -like "*DigitalFTE*"} | Select-Object -First 10
```

### Troubleshooting

**Task not running:**
1. Check task is enabled: Task Scheduler → DigitalFTE → Right-click task → Enable
2. Verify Python path: Task properties → Actions → Edit
3. Check working directory: Task properties → Actions → Start in
4. Review logs: `logs/run_agent_*.log`

**Permission errors:**
1. Run Task Scheduler as Administrator
2. Task properties → General → "Run with highest privileges"

**Network errors:**
1. Task properties → Conditions → "Start only if network available"

## Linux/macOS Cron Setup

### Automatic Setup

```bash
chmod +x scheduler/cron/setup_scheduler.sh
./scheduler/cron/setup_scheduler.sh
```

This will:
1. Check Python installation
2. Create logs directory
3. Prepare crontab entries
4. Backup existing crontab
5. Install new cron jobs
6. Verify installation

### Manual Setup

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
*/5 * * * * cd /path/to/silver-tier && python3 run_agent.py watchers >> logs/cron_watchers.log 2>&1
0 9 * * 1 cd /path/to/silver-tier && python3 run_agent.py ceo-report >> logs/cron_ceo_report.log 2>&1
```

### Cron Jobs

**Watchers**
- **Schedule**: `*/5 * * * *` (every 5 minutes)
- **Command**: `python3 run_agent.py watchers`
- **Log**: `logs/cron_watchers.log`

**CEO Report**
- **Schedule**: `0 9 * * 1` (Monday 9:00 AM)
- **Command**: `python3 run_agent.py ceo-report`
- **Log**: `logs/cron_ceo_report.log`

### Verification

```bash
# List cron jobs
crontab -l

# Check cron service status
sudo systemctl status cron     # Debian/Ubuntu
sudo systemctl status crond    # CentOS/RHEL

# View cron logs
tail -f logs/cron_watchers.log
tail -f logs/cron_ceo_report.log

# System cron logs
grep CRON /var/log/syslog      # Debian/Ubuntu
grep CRON /var/log/cron        # CentOS/RHEL
```

### Troubleshooting

**Cron jobs not running:**
1. Check cron service: `sudo systemctl status cron`
2. Verify crontab: `crontab -l`
3. Check permissions: `ls -la run_agent.py`
4. Review logs: `tail -f logs/cron_watchers.log`

**Environment issues:**
1. Add full paths to crontab (Python, project directory)
2. Set environment variables in crontab:
   ```
   PATH=/usr/local/bin:/usr/bin:/bin
   PYTHON=/usr/bin/python3
   ```

**Permission errors:**
1. Make script executable: `chmod +x run_agent.py`
2. Check log directory: `mkdir -p logs && chmod 755 logs`

## Logging

### Log Files

```
logs/
├── run_agent_20260213.log        # Daily orchestration log
├── cron_watchers.log             # Cron watchers log (Linux)
├── cron_ceo_report.log           # Cron CEO report log (Linux)
├── file_watcher.log              # File watcher service log
├── gmail_watcher.log             # Gmail watcher service log
└── email-server.log              # MCP email server log
```

### Log Format

```
2026-02-13 15:30:00 [INFO] run_agent: Running all watchers
2026-02-13 15:30:01 [INFO] run_agent: Starting file watcher...
2026-02-13 15:30:02 [INFO] run_agent: Found 3 file(s) in Inbox
2026-02-13 15:30:05 [INFO] run_agent: File watcher result: {'files_processed': 3}
```

### Viewing Logs

```bash
# Tail logs in real-time
tail -f logs/run_agent_*.log

# View last 50 lines
tail -50 logs/run_agent_*.log

# Search logs
grep "ERROR" logs/run_agent_*.log
grep "watchers" logs/run_agent_*.log

# View logs by date
ls -lt logs/run_agent_*.log | head -5
```

## Testing

### Manual Testing

```bash
# Test watchers
python run_agent.py watchers

# Test CEO report
python run_agent.py ceo-report

# Test with debug logging
python run_agent.py watchers --log-level DEBUG
```

### Expected Output

```
======================================================================
Silver Tier Digital FTE - Agent Orchestration
======================================================================
Command: watchers
Timestamp: 2026-02-13T15:30:00
======================================================================
Running all watchers
======================================================================
Starting file watcher...
Found 3 file(s) in Inbox
Processing: task1.md
Processing: task2.md
Processing: task3.md
File watcher result: {'files_processed': 3}
Starting Gmail watcher...
Checking for unread emails...
Gmail watcher result: {'emails_processed': 2}
======================================================================
Watchers completed: True
======================================================================
Duration: 12.34 seconds
```

### Validation Script

```bash
# Create test file
echo "Test task" > memory/Inbox/test_task.md

# Run watchers
python run_agent.py watchers

# Check logs
tail -20 logs/run_agent_*.log

# Verify file was processed
ls memory/Inbox/  # Should be empty or file moved
```

## Configuration

### Environment Variables

```bash
# CEO email address (for reports)
export CEO_EMAIL=ceo@company.com

# Log level
export LOG_LEVEL=INFO

# Python path (for cron)
export PYTHON=/usr/bin/python3
```

### Customization

**Change watcher frequency:**

Windows: Edit `run_watchers.xml`
```xml
<Interval>PT10M</Interval>  <!-- Change to 10 minutes -->
```

Linux: Edit crontab
```bash
*/10 * * * *  # Change to every 10 minutes
```

**Change CEO report schedule:**

Windows: Edit `ceo_report.xml`
```xml
<DaysOfWeek>
  <Friday />  <!-- Change to Friday -->
</DaysOfWeek>
```

Linux: Edit crontab
```bash
0 9 * * 5  # Change to Friday
```

## Monitoring

### Health Checks

```bash
# Check if tasks are running
ps aux | grep run_agent.py

# Check last execution time
ls -lt logs/run_agent_*.log | head -1

# Check for errors
grep -i error logs/run_agent_*.log | tail -20
```

### Alerts

Set up alerts for:
- Task failures (exit code != 0)
- No execution in expected timeframe
- Error patterns in logs
- Disk space for logs

### Metrics

Track:
- Execution frequency
- Success rate
- Average duration
- Files processed
- Emails sent

## Uninstallation

### Windows

```powershell
# Remove tasks
Unregister-ScheduledTask -TaskName "DigitalFTE\RunWatchers" -Confirm:$false
Unregister-ScheduledTask -TaskName "DigitalFTE\CEOReport" -Confirm:$false

# Remove folder (if empty)
# Task Scheduler → Delete \DigitalFTE folder
```

### Linux

```bash
# Edit crontab
crontab -e

# Remove Digital FTE entries (lines with "run_agent.py")

# Or restore backup
crontab scheduler/cron/crontab_backup_*.txt
```

## Best Practices

1. **Test before scheduling**: Run commands manually first
2. **Monitor logs**: Check logs regularly for errors
3. **Backup crontab**: Keep backups before changes
4. **Use absolute paths**: Avoid relative paths in scheduled tasks
5. **Set timeouts**: Prevent tasks from running indefinitely
6. **Handle failures**: Implement retry logic and alerts
7. **Rotate logs**: Clean up old log files periodically
8. **Document changes**: Keep notes on schedule modifications

## Support

For issues:
1. Check logs: `logs/run_agent_*.log`
2. Test manually: `python run_agent.py watchers`
3. Verify configuration: Task Scheduler or `crontab -l`
4. Review documentation: This README

## Changelog

### v1.0.0 (2026-02-13)
- Initial release
- Windows Task Scheduler support
- Linux cron support
- Automated setup scripts
- Comprehensive logging
- CEO report generation
