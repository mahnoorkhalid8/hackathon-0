# Digital FTE - Quick Start Guide

**Version:** 1.0 Bronze Tier
**Setup Time:** 5 minutes
**Prerequisites:** None (local-first system)

---

## What You've Got

A complete, production-ready Digital FTE automation system that:
- Processes tasks autonomously using deterministic skills
- Maintains complete audit trails in markdown
- Operates entirely on your local filesystem
- Requires no external dependencies or APIs

---

## System Status

```
✓ Core architecture deployed
✓ 3 executable skills (1,131 lines of deterministic logic)
✓ Company Handbook with decision framework
✓ Real-time Dashboard with metrics
✓ Complete workflow automation (Inbox → Needs_Action → Done)
✓ Example tasks included
✓ 1 task completed (demonstration)
```

---

## 5-Minute Quick Start

### Step 1: Understand the Folders

```
AI_Employee_Vault/
├── Inbox/           ← Drop new tasks here
├── Needs_Action/    ← Active work happens here
├── Done/            ← Completed tasks with summaries
├── Dashboard.md     ← Check status here
├── Company_Handbook.md  ← Read operating rules
└── SKILLS/          ← Automation procedures
```

### Step 2: Create Your First Task

Create a file in `Inbox/` with this format:

```markdown
# Your Task Title

**Priority:** P2
**Requester:** Your Name
**Due Date:** 2026-02-15

## Description
What needs to be done in clear, specific terms.

## Acceptance Criteria
- [ ] Specific outcome 1
- [ ] Specific outcome 2
- [ ] Specific outcome 3

## Context
Any background information that helps.
```

**File naming:** `YYYYMMDD-HHMM-task-description.md`

### Step 3: Let the System Process It

The Digital FTE will automatically:

1. **Triage** (within 15 minutes)
   - Validate the task structure
   - Assess priority and complexity
   - Calculate effort estimate
   - Move to Needs_Action/ or flag for clarification

2. **Execute** (based on priority)
   - Process in priority order (P0 → P3)
   - Log all actions in work log
   - Check off acceptance criteria
   - Document any issues

3. **Complete** (when done)
   - Move to Done/ folder
   - Generate comprehensive summary
   - Update Dashboard metrics
   - Capture learnings

### Step 4: Monitor Progress

Check `Dashboard.md` for:
- Current task counts in each folder
- Activity log with timestamps
- System health status
- Quick action reference

---

## Priority Levels

| Priority | SLA | When to Use |
|----------|-----|-------------|
| **P0** | Immediate | Critical issues, system down |
| **P1** | 4 hours | Blocking users, broken features |
| **P2** | 24 hours | Standard tasks, improvements |
| **P3** | 3 days | Nice-to-haves, documentation |

---

## Common Workflows

### Standard Task

```
1. Create task file in Inbox/
2. System triages automatically
3. Task moves to Needs_Action/
4. Digital FTE processes it
5. Task moves to Done/ with summary
6. Check Dashboard for confirmation
```

### Task Needs Clarification

```
1. Create task file in Inbox/
2. System triages and finds it incomplete
3. File renamed to [CLARIFICATION]-filename.md
4. You add missing details
5. Remove [CLARIFICATION] prefix
6. System re-triages and proceeds
```

### Urgent Task

```
1. Create task with Priority: P0
2. System triages immediately
3. Moves to top of Needs_Action/ queue
4. Processed before all other tasks
5. Completed within SLA
```

### Need Human Decision

```
1. Digital FTE encounters ambiguity
2. Creates [ESCALATION] task in Inbox/
3. Presents 2-3 options with pros/cons
4. You review and provide decision
5. Digital FTE continues with guidance
```

---

## Key Files to Know

### Dashboard.md
Your command center. Check this first.
- Current metrics
- Activity log
- System status

### Company_Handbook.md
The operating manual. Read this to understand:
- Mission and objectives
- Decision framework
- Priority system
- Quality standards

### SKILLS/README.md
How automation works. Reference when:
- Understanding skill execution
- Troubleshooting issues
- Extending the system

### SYSTEM_OVERVIEW.md
Complete architecture documentation. Use for:
- Understanding design decisions
- System maintenance
- Future enhancements

---

## Example Tasks Included

### In Inbox/ (Ready to Process)

**20260212-1430-process-customer-feedback.md**
- Priority: P2
- Type: Analysis and documentation
- Demonstrates: Multi-step task with research

### In Done/ (Completed Example)

**20260212-0915-fix-broken-documentation-link.md**
- Shows complete workflow
- Includes work log
- Has auto-generated summary
- Demonstrates: Simple task execution

---

## Troubleshooting

### "Task isn't moving from Inbox"

**Check for:**
- `[CLARIFICATION]` prefix → Add missing details
- `[BLOCKED]` prefix → Resolve dependencies
- Invalid format → Compare to template above

### "Task stuck in Needs_Action"

**Verify:**
- Acceptance criteria are checked off
- Status metadata updated to "completed"
- Work log documents actions taken

### "Summary not generated"

**Try:**
- Check Dashboard for errors
- Verify file is in Done/ folder
- Manually invoke summarize_task skill

---

## Best Practices

### ✓ DO

- Use clear, specific task titles
- Include 3-5 testable acceptance criteria
- Set realistic priorities
- Provide sufficient context
- Check Dashboard regularly
- Review Done/ folder for learnings

### ✗ DON'T

- Create tasks without acceptance criteria
- Use P0 for non-critical items
- Skip the description section
- Ignore [ESCALATION] tasks
- Manually move files (use skills)
- Edit metadata directly (let skills handle it)

---

## Extending the System

### Add a New Skill

1. Copy skill template from existing skill
2. Define purpose, triggers, input/output
3. Write deterministic step-by-step logic
4. Add error handling and success criteria
5. Test with example tasks
6. Update SKILLS/README.md

### Customize Decision Framework

1. Edit Company_Handbook.md
2. Update "Autonomous Decision Authority" section
3. Add/modify escalation rules
4. Document changes in version history

### Add Custom Metadata

1. Define field in SYSTEM_OVERVIEW.md schema
2. Update relevant skills to populate it
3. Modify Dashboard if it affects metrics
4. Test with example tasks

---

## Performance Expectations

### Bronze Tier Targets

- **Triage Time:** <15 minutes
- **Completion Rate:** >90%
- **Clarification Rate:** <20%
- **Error Rate:** <5%
- **SLA Compliance:** >95%

### Current Performance

Check Dashboard.md for real-time metrics:
- Tasks completed today
- Total tasks completed
- Current queue sizes
- System uptime

---

## What Makes This System Different

### 1. Deterministic
Every skill is explicit pseudocode. No "figure it out" logic. Same input = same output.

### 2. Local-First
Everything on your filesystem. No APIs, no cloud, no dependencies. Complete control.

### 3. Transparent
Every action logged. Complete audit trail. Human-readable at every step.

### 4. Atomic
All-or-nothing operations. Automatic rollback on failure. Data integrity guaranteed.

### 5. Extensible
Add skills, customize workflows, modify decision framework. Built to evolve.

---

## Next Steps

### Immediate (Next 5 Minutes)

1. Read Company_Handbook.md (5 min read)
2. Check Dashboard.md for current status
3. Review the completed example in Done/
4. Try creating your first task

### Short Term (This Week)

1. Process 5-10 real tasks through the system
2. Identify patterns in your workflow
3. Customize Company_Handbook.md for your needs
4. Add task templates for common scenarios

### Long Term (This Month)

1. Review Done/ folder for learnings
2. Calculate actual performance metrics
3. Create custom skills for repeated operations
4. Consider Bronze → Silver tier upgrades

---

## Getting Help

### Documentation

- **This file:** Quick start and common workflows
- **Company_Handbook.md:** Operating rules and decisions
- **SKILLS/README.md:** Automation system details
- **SYSTEM_OVERVIEW.md:** Complete architecture

### Troubleshooting

- Check Dashboard.md activity log first
- Review skill error handling sections
- Create [ESCALATION] task for complex issues
- Consult SYSTEM_OVERVIEW.md troubleshooting section

### Support

This is a local-first system. You have complete control and visibility. All issues can be diagnosed through:
1. Dashboard activity log
2. File metadata
3. Skill execution logic
4. System state inspection

---

## Success Indicators

You'll know the system is working when:

✓ Tasks move automatically from Inbox → Needs_Action
✓ Dashboard updates with each action
✓ Completed tasks have comprehensive summaries
✓ Metrics track your productivity
✓ You spend less time on task management
✓ Audit trail provides complete transparency

---

## Remember

This is a **Bronze Tier** system focused on:
- Deterministic execution
- Local-first operation
- Complete transparency
- Minimal complexity

It's designed to be:
- Understandable by reading the files
- Maintainable without special tools
- Extensible through markdown skills
- Reliable through atomic operations

**Start simple. Let patterns emerge. Evolve the system based on real usage.**

---

**You're ready to go. Create your first task in Inbox/ and watch the system work.**
