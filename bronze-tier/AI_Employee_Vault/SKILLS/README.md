# SKILLS System - Digital FTE

**Version:** 1.0
**Tier:** Bronze
**Last Updated:** 2026-02-12

---

## Overview

The SKILLS system provides deterministic, executable procedures for the Digital FTE to process tasks autonomously. Each skill is a self-contained Markdown file with explicit step-by-step reasoning that any agent can follow without ambiguity.

---

## Available Skills

### Core Workflow Skills

| Skill | Purpose | Trigger | Execution |
|-------|---------|---------|-----------|
| **triage_file.md** | Assess and route incoming tasks | New file in Inbox/ | Automatic (15min) |
| **summarize_task.md** | Generate completion summaries | File moved to Done/ | Automatic |
| **move_to_folder.md** | Safe file movement with audit trail | Workflow transitions | Manual/Automatic |

---

## Skill Architecture

Each skill follows a standardized structure:

```markdown
# Skill: [Name]

## Purpose
Clear statement of what the skill does

## Trigger Condition
Explicit conditions that invoke the skill

## Input Format
Required data structure and validation rules

## Output Format
Expected results and side effects

## Step-by-Step Reasoning Process
Deterministic pseudocode (IF/THEN/FOR/WHILE)
- No ambiguous instructions
- Explicit validation at each step
- Clear error handling

## Success Criteria
Testable assertions for verification

## Error Handling
Specific rollback procedures for each failure mode
```

---

## Workflow Integration

### Task Lifecycle

```
1. INTAKE
   ├─ Task file created in Inbox/
   ├─ [triage_file] executes automatically
   ├─ Validates structure and completeness
   └─ Routes to Needs_Action/ or flags for clarification

2. EXECUTION
   ├─ Task file in Needs_Action/
   ├─ Digital FTE processes task
   ├─ Updates work log inline
   └─ Marks acceptance criteria as completed

3. COMPLETION
   ├─ [move_to_folder] moves file to Done/
   ├─ [summarize_task] executes automatically
   ├─ Generates summary with outcomes
   └─ Updates Dashboard metrics
```

### Skill Invocation

**Automatic Triggers:**
- `triage_file` → New file detected in Inbox/
- `summarize_task` → File moved to Done/
- `move_to_folder` → Called by other skills during transitions

**Manual Invocation:**
- Reference skill by name: "Execute triage_file on task-123.md"
- Provide required parameters per skill's Input Format
- Skill validates inputs before execution

---

## Using Skills

### For Digital FTE Agents

1. **Read the skill file completely** before execution
2. **Follow the step-by-step reasoning** exactly as written
3. **Validate inputs** per the Input Format section
4. **Execute each step** in sequence (no skipping)
5. **Check success criteria** after completion
6. **Handle errors** per the Error Handling section
7. **Log all actions** to Dashboard

### For Human Operators

1. **Create task files** following the format in triage_file.md
2. **Drop files in Inbox/** and let automation handle routing
3. **Monitor Dashboard.md** for status updates
4. **Review Done/** folder for completed work summaries
5. **Check for [CLARIFICATION] or [BLOCKED]** prefixes in Inbox/

---

## Task File Format

### Minimum Required Structure

```markdown
# Task Title

**Priority:** P0|P1|P2|P3
**Requester:** Name or System
**Due Date:** YYYY-MM-DD or "None"

## Description
Clear explanation of what needs to be done

## Acceptance Criteria
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

## Context
Optional background information
```

### Example Task File

```markdown
# Update Customer Dashboard Widget

**Priority:** P1
**Requester:** Product Team
**Due Date:** 2026-02-15

## Description
The customer dashboard needs a new widget showing monthly usage trends.
Widget should display last 6 months of data with a line chart.

## Acceptance Criteria
- [ ] Widget displays on customer dashboard page
- [ ] Shows last 6 months of usage data
- [ ] Line chart renders correctly
- [ ] Data updates daily at midnight
- [ ] Mobile responsive design

## Context
This is part of the Q1 customer visibility initiative.
Design mockups are in Figma (link: figma.com/file/abc123).
```

---

## Skill Execution Guarantees

### Deterministic Behavior
- Same input → Same output (no randomness)
- Explicit decision trees (no "figure it out")
- Predictable error handling

### Atomic Operations
- All-or-nothing execution
- Rollback on failure
- No partial state changes

### Audit Trail
- Every action logged to Dashboard
- Metadata tracking in file headers
- Complete history in Done/ folder

### Validation
- Input validation before execution
- State verification during execution
- Output validation after execution

---

## Extending the SKILLS System

### Adding New Skills

1. **Copy the skill template structure**
2. **Define clear Purpose and Trigger Conditions**
3. **Specify exact Input/Output formats**
4. **Write deterministic reasoning in pseudocode**
5. **Include comprehensive error handling**
6. **Add testable success criteria**
7. **Update this README with the new skill**

### Skill Design Principles

**DO:**
- Use explicit pseudocode (IF/THEN/FOR/WHILE)
- Validate inputs at every step
- Handle all error cases explicitly
- Make operations atomic and reversible
- Log all actions for audit trail

**DON'T:**
- Use vague instructions ("handle appropriately")
- Assume implicit behavior
- Skip validation steps
- Leave error cases unhandled
- Make irreversible changes without confirmation

---

## Troubleshooting

### Skill Not Executing

**Check:**
- [ ] Trigger condition is met
- [ ] Input format matches specification
- [ ] Required folders exist (Inbox, Needs_Action, Done)
- [ ] File permissions allow read/write
- [ ] Dashboard.md is accessible

### Skill Execution Failed

**Review:**
- [ ] Error message in Dashboard activity log
- [ ] File metadata for error details
- [ ] Success criteria validation results
- [ ] Rollback operations completed

### Task Stuck in Inbox

**Possible Causes:**
- File has `[CLARIFICATION]` prefix → Needs more details
- File has `[BLOCKED]` prefix → Has dependencies
- File structure invalid → Check format requirements
- Triage skill failed → Check Dashboard for errors

---

## Performance Metrics

Track these metrics in Dashboard.md:

- **Triage Time:** Time from file creation to routing (target: <15min)
- **Completion Rate:** % of tasks reaching Done/ (target: >90%)
- **Clarification Rate:** % of tasks needing clarification (target: <20%)
- **Error Rate:** % of skill executions failing (target: <5%)

---

## Version History

**1.0 (2026-02-12)**
- Initial release with 3 core skills
- triage_file: Intake and routing
- summarize_task: Completion documentation
- move_to_folder: Safe file operations

---

## Support

For issues or questions:
1. Check Dashboard.md activity log
2. Review skill file for error handling guidance
3. Create escalation task in Inbox/ with `[ESCALATION]` prefix
4. Reference Company_Handbook.md for decision framework

---

**Remember:** Skills are deterministic procedures. If a skill isn't working as expected, the issue is either in the input format, trigger condition, or execution environment—never in the skill's reasoning process itself.
