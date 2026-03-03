# Silver Tier Digital FTE - Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify directory structure:**
   ```bash
   ls -la memory/
   ls -la config/
   ls -la watchers/
   ```

## Running the System

### Option 1: Normal Operation

```bash
python main.py
```

This starts the full system with all configured watchers.

### Option 2: Demo Mode

```bash
python demo.py
```

This runs a 30-second demonstration showing the system in action.

## First Steps

### 1. Create a Task

Create a file in `memory/Inbox/my-task.md`:

```markdown
# Task: Generate Status Report

Please create a status report for today.

**Type:** scheduled_report
**Priority:** normal
```

### 2. Monitor Processing

Watch the console output to see:
- File watcher detecting the new file
- Context being loaded
- Reasoning engine analyzing the task
- Task being routed to appropriate queue

### 3. Check Dashboard

Open `memory/Dashboard.md` to see:
- Current system state
- Active tasks
- Recent activity
- Pending approvals

### 4. Review Reasoning

Open `memory/Plan.md` to see:
- Current situation analysis
- Step-by-step reasoning
- Decision made
- Confidence level

### 5. Handle Approvals

If task requires approval:
1. Open file in `memory/Needs_Approval/`
2. Review the reasoning
3. Add your decision:
   ```markdown
   ## APPROVAL DECISION
   Status: APPROVED
   Notes: Looks good
   ```
4. Move to `memory/Needs_Action/` for execution

## Configuration

### Enable/Disable Watchers

Edit `config/fte_config.yaml`:

```yaml
watchers:
  file_watcher:
    enabled: true  # Set to false to disable
  time_watcher:
    enabled: true
```

### Adjust Approval Rules

Edit `config/approval_rules.yaml`:

```yaml
auto_approve:
  - skill: "email_responder"
    conditions:
      sentiment: ["positive", "neutral"]
```

### Add Scheduled Tasks

Edit `scheduler/schedule_config.yaml`:

```yaml
scheduled_tasks:
  - id: "my_task"
    name: "My Daily Task"
    type: "daily"
    time: "09:00"
    enabled: true
```

## Monitoring

### Real-time Status

The console shows:
- Events detected
- Processing steps
- Task routing decisions
- Execution results

### Dashboard

`memory/Dashboard.md` shows:
- Active task count
- Completed tasks
- Pending approvals
- System health
- Recent activity

### Logs

Check `logs/` directory:
- `system.log` - General system logs
- `decisions.log` - Reasoning decisions
- `actions.log` - Executed actions

## Troubleshooting

### No Events Detected

- Verify watchers are enabled in config
- Check watch paths exist
- Ensure file patterns match (*.md)

### Tasks Not Executing

- Check if task is in Needs_Approval/ (requires human review)
- Verify skill definition exists
- Check logs for errors

### Dashboard Not Updating

- Ensure write permissions on memory/ directory
- Check for errors in console output
- Verify state_manager is running

## Architecture

```
Trigger → Orchestrator → Context → Reasoning → Router
                                                   ↓
                                    Needs_Action ← → Needs_Approval
                                         ↓                  ↓
                                    Executor          (Human Review)
                                         ↓                  ↓
                                    Done/ ← ← ← ← ← ← ← ← ←
```

## Next Steps

1. **Customize Skills**: Add your own skills in `memory/SKILLS/`
2. **Configure Approval Rules**: Adjust what requires approval
3. **Add MCP Servers**: Enable external integrations
4. **Schedule Tasks**: Set up recurring operations
5. **Monitor & Iterate**: Review logs and optimize

## Support

- Check README.md for detailed documentation
- Review example skills in memory/SKILLS/
- Examine config files for all options
