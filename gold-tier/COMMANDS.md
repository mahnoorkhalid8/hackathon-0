# Digital FTE - Quick Command Reference

## Two Ways to Monitor Your System

### 1. Continuous Monitoring (Real-Time)
**File:** `inbox_watcher.py`
**Purpose:** Watches Inbox folder continuously and auto-processes new files

**Run:**
```bash
python inbox_watcher.py
```

**What it does:**
- Monitors `AI_Employee_Vault/Inbox/` in real-time
- Detects new .md files instantly (<1 second)
- Automatically triages via Claude CLI
- Adds metadata to files
- Routes to Needs_Action/Done
- Updates Dashboard
- Runs until you stop it (Ctrl+C)

**When to use:**
- When you want automatic processing
- For continuous operation
- When dropping multiple tasks over time

---

### 2. One-Time Check (On-Demand)
**File:** `orchestrator.py`
**Purpose:** Checks current system state and shows what needs attention

**Run:**
```bash
python orchestrator.py
```

**What it does:**
- Checks system health
- Counts files in each folder
- Lists pending tasks
- Shows Dashboard summary
- Suggests next actions
- Exits immediately after check

**When to use:**
- To see current system status
- Before starting work
- To check what needs attention
- For quick status updates

---

## Quick Start Commands

### Check System Status
```bash
python orchestrator.py
```

### Start Continuous Monitoring
```bash
python inbox_watcher.py
```

### Create a Test Task
```bash
# Windows PowerShell
@"
# Test Task

**Priority:** P2
**Requester:** Me
**Due Date:** 2026-02-15

## Description
Test the Digital FTE system.

## Acceptance Criteria
- [ ] Task triaged automatically
- [ ] Metadata added
- [ ] File moved to Needs_Action
"@ | Out-File -FilePath "AI_Employee_Vault\Inbox\test-task.md" -Encoding UTF8
```

### Check Dashboard
```bash
cat AI_Employee_Vault\Dashboard.md
```

---

## Typical Workflow

**Morning routine:**
```bash
# 1. Check what needs attention
python orchestrator.py

# 2. Start continuous monitoring
python inbox_watcher.py
```

**During the day:**
- Drop tasks in `AI_Employee_Vault\Inbox\`
- Watcher processes them automatically
- Check Dashboard for status

**End of day:**
```bash
# Stop watcher (Ctrl+C)
# Run final check
python orchestrator.py
```

---

## Expected Output

### orchestrator.py
```
============================================================
              Digital FTE Orchestrator
============================================================

▶ System Health Check
  ✓ AI_Employee_Vault/ exists
  ✓ Inbox/ exists
  ✓ Needs_Action/ exists
  ✓ Done/ exists
  ✓ Dashboard.md exists

▶ Folder Analysis
  ℹ Inbox: 2 file(s)
    - task1.md
    - task2.md
  ℹ Needs_Action: 1 file(s)
    - active-task.md
  ℹ Done: 5 file(s)

▶ Pending Tasks
  ⚠ 2 task(s) awaiting triage in Inbox

▶ Suggested Next Actions
  1. Start inbox_watcher.py to auto-triage 2 task(s)
```

### inbox_watcher.py
```
============================================================
Digital FTE Inbox Watcher Starting
============================================================

Monitoring: C:\Users\...\AI_Employee_Vault\Inbox
Watcher active. Press Ctrl+C to stop.

2026-02-12 10:00:00 - INFO - New file detected: task.md
2026-02-12 10:00:02 - INFO - Processing: task.md
2026-02-12 10:00:02 - INFO - Calling Claude Code CLI for triage
2026-02-12 10:00:10 - INFO - Triage complete: task.md → needs_action
2026-02-12 10:00:10 - INFO - Moved task.md → Needs_Action/
```

---

## Troubleshooting

### orchestrator.py shows errors
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

### inbox_watcher.py not detecting files
```bash
# Check if watcher is running
# Check if file is .md extension
# Check if file is in correct folder
```

### Claude CLI not found
```bash
# Install Claude Code CLI first
# Verify: claude --version
```

---

## Quick Tips

1. **Always run orchestrator.py first** to see system status
2. **Use inbox_watcher.py for automation** - let it run in background
3. **Check Dashboard.md** for real-time metrics
4. **Create tasks with proper format** (see QUICK_START.md)
5. **Stop watcher with Ctrl+C** when done

---

**Ready to start? Run:**
```bash
python orchestrator.py
```
