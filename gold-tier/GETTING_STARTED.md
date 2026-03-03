# Digital FTE - Your Two Commands

## ✅ System Ready!

You now have **2 commands** to manage your Digital FTE system:

---

## Command 1: Check System Status (One-Time)

**File:** `orchestrator.py`

**Run:**
```bash
python orchestrator.py
```

**What it shows:**
- ✓ System health (all folders exist)
- ✓ File counts in each folder
- ✓ Pending tasks that need attention
- ✓ Dashboard summary
- ✓ Suggested next actions

**Current Status:**
```
[OK] System healthy
[!] 1 task awaiting triage in Inbox
[i] 0 tasks in Needs_Action
[i] 1 task completed in Done
```

---

## Command 2: Continuous Monitoring (Real-Time)

**File:** `inbox_watcher.py`

**Run:**
```bash
python inbox_watcher.py
```

**What it does:**
- Watches Inbox folder continuously
- Auto-detects new .md files
- Calls Claude CLI for triage
- Adds metadata automatically
- Routes files to correct folder
- Updates Dashboard
- Runs until you stop it (Ctrl+C)

**Note:** Requires Claude CLI installed (`claude --version`)

---

## Quick Start Workflow

### Step 1: Check Current Status
```bash
python orchestrator.py
```

**Output shows:**
- 1 task waiting in Inbox
- Suggests: "Start inbox_watcher.py to auto-triage"

### Step 2: Start Continuous Monitoring
```bash
python inbox_watcher.py
```

**It will:**
- Process the existing task in Inbox
- Watch for new tasks
- Auto-triage everything

### Step 3: Create a New Task (While Watcher Runs)

**Open another terminal and create:**
```bash
# Create test-task.md in Inbox folder
notepad AI_Employee_Vault\Inbox\test-task.md
```

**Add this content:**
```markdown
# Test Task

**Priority:** P2
**Requester:** Me
**Due Date:** 2026-02-15

## Description
Test the automatic triage system.

## Acceptance Criteria
- [ ] Task is detected
- [ ] Metadata is added
- [ ] File moves to Needs_Action
```

**Save and close** - the watcher will process it automatically!

### Step 4: Check Results
```bash
# Stop watcher (Ctrl+C)
# Run status check
python orchestrator.py
```

---

## What You'll See

### orchestrator.py Output:
```
============================================================
              Digital FTE Orchestrator
============================================================

>> System Health Check
  [OK] AI_Employee_Vault/ exists
  [OK] Inbox/ exists
  [OK] Needs_Action/ exists
  [OK] Done/ exists
  [OK] Dashboard.md exists

>> Folder Analysis
  [i] Inbox: 1 file(s)
  [i] Needs_Action: 0 file(s)
  [i] Done: 1 file(s)

>> Pending Tasks
  [!] 1 task(s) awaiting triage in Inbox

>> Suggested Next Actions
  1. Start inbox_watcher.py to auto-triage 1 task(s)

============================================================
                        Summary
============================================================
  Total tasks in system: 2
  Pending attention: 1
  [!] Action required: 1 task(s) need attention
```

### inbox_watcher.py Output:
```
============================================================
Digital FTE Inbox Watcher Starting
============================================================

Monitoring: C:\Users\...\AI_Employee_Vault\Inbox
Watcher active. Press Ctrl+C to stop.

2026-02-12 10:00:00 - INFO - New file detected: test-task.md
2026-02-12 10:00:02 - INFO - Processing: test-task.md
2026-02-12 10:00:02 - INFO - Calling Claude Code CLI for triage
2026-02-12 10:00:10 - INFO - Triage complete: test-task.md → needs_action
2026-02-12 10:00:10 - INFO - Moved test-task.md → Needs_Action/
```

---

## Typical Daily Workflow

**Morning:**
```bash
# Check what needs attention
python orchestrator.py

# Start continuous monitoring
python inbox_watcher.py
```

**During the day:**
- Drop tasks in `AI_Employee_Vault\Inbox\`
- Watcher processes them automatically
- Check Dashboard: `cat AI_Employee_Vault\Dashboard.md`

**End of day:**
```bash
# Stop watcher (Ctrl+C)
# Final status check
python orchestrator.py
```

---

## Troubleshooting

### orchestrator.py Issues
```bash
# If Python not found
python --version
# or try
py orchestrator.py

# If dependencies missing
pip install -r requirements.txt
```

### inbox_watcher.py Issues
```bash
# If Claude CLI not found (optional)
# You can still use manual mode
# Or install Claude CLI from: https://claude.ai/download

# Check if watcher is running
# Look for: "Watcher active. Press Ctrl+C to stop."
```

---

## Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `python orchestrator.py` | Check status | Anytime you want to see what needs attention |
| `python inbox_watcher.py` | Auto-process | When you want continuous automation |

---

## Next Steps

1. **Run orchestrator** to see current status:
   ```bash
   python orchestrator.py
   ```

2. **Start watcher** for automation:
   ```bash
   python inbox_watcher.py
   ```

3. **Create a test task** in Inbox folder

4. **Watch it process** automatically!

---

**Both commands are ready to use. Start with `python orchestrator.py` to see your system status!**
