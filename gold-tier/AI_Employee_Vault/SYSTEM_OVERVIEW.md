# Digital FTE System - Architecture Overview

**Version:** 1.0
**Tier:** Bronze
**Created:** 2026-02-12
**Status:** Production Ready

---

## System Purpose

A local-first, deterministic Digital FTE (Full-Time Employee) automation system that processes tasks autonomously using explicit, executable procedures defined in Markdown skill files.

---

## Architecture Principles

### 1. Local-First
- All data stored in local filesystem
- No external dependencies or APIs required
- Complete audit trail in markdown files
- Human-readable formats throughout

### 2. Deterministic Execution
- Skills written as explicit pseudocode
- Same input always produces same output
- No ambiguous instructions or "figure it out" logic
- Predictable, testable behavior

### 3. Transparency
- Every action logged to Dashboard
- Complete metadata tracking in file headers
- Audit trail preserved in Done/ folder
- Human-readable at every step

### 4. Atomic Operations
- All-or-nothing execution
- Rollback on failure
- No partial state changes
- Data integrity guaranteed

---

## System Components

### Core Files

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status and activity log
├── Company_Handbook.md       # Operating rules and decision framework
├── Inbox/                    # New tasks arrive here
├── Needs_Action/            # Active work in progress
├── Done/                    # Completed tasks with summaries
└── SKILLS/                  # Executable skill procedures
    ├── README.md            # Skills documentation
    ├── triage_file.md       # Intake and routing
    ├── summarize_task.md    # Completion documentation
    └── move_to_folder.md    # Safe file operations
```

### Component Responsibilities

**Dashboard.md**
- Current system metrics (tasks in each folder)
- Activity log with timestamps
- System health indicators
- Quick action reference

**Company_Handbook.md**
- Mission and core objectives
- Communication style guidelines
- Task processing workflow (3 stages)
- Decision framework (autonomous vs escalation)
- Priority levels and SLAs
- Quality standards

**Inbox/**
- Entry point for all new tasks
- Tasks await triage (15-minute SLA)
- Flagged tasks remain with prefix:
  - `[CLARIFICATION]` - needs more details
  - `[BLOCKED]` - has dependencies

**Needs_Action/**
- Tasks ready for execution
- Processed in priority order (P0 → P3)
- Work log updated inline during execution
- Acceptance criteria checked off as completed

**Done/**
- Archive of completed tasks
- Includes auto-generated summaries
- Complete audit trail with metadata
- Source for metrics and learnings

**SKILLS/**
- Deterministic procedures for automation
- Each skill is self-contained
- Explicit step-by-step reasoning
- Comprehensive error handling

---

## Task Lifecycle

### Stage 1: Intake (Inbox/)

```
1. Task file created in Inbox/
   ├─ Format: YYYYMMDD-HHMM-description.md
   ├─ Contains: Title, Priority, Description, Acceptance Criteria
   └─ Trigger: File creation

2. Triage Skill Executes (automatic, <15min)
   ├─ Validates file structure
   ├─ Assesses priority (P0-P3)
   ├─ Evaluates completeness (0-100 score)
   ├─ Calculates complexity (simple/moderate/complex)
   ├─ Estimates effort (15min to 3 days)
   ├─ Checks for blockers
   └─ Adds metadata to file header

3. Routing Decision
   ├─ If actionable → Move to Needs_Action/
   ├─ If incomplete → Rename with [CLARIFICATION] prefix
   └─ If blocked → Rename with [BLOCKED] prefix
```

### Stage 2: Execution (Needs_Action/)

```
1. Task Selection
   ├─ Priority order: P0 > P1 > P2 > P3
   ├─ Within priority: oldest first
   └─ Update status to "in_progress"

2. Work Execution
   ├─ Add started_at timestamp
   ├─ Log actions in Work Log section
   ├─ Check off acceptance criteria as completed
   └─ Document any blockers or issues

3. Completion Check
   ├─ All acceptance criteria met?
   ├─ Quality standards satisfied?
   ├─ Documentation complete?
   └─ Ready for Done/ folder
```

### Stage 3: Completion (Done/)

```
1. Move to Done (move_to_folder skill)
   ├─ Update metadata (completed_at, moved_at)
   ├─ Execute atomic move operation
   └─ Verify file integrity

2. Generate Summary (summarize_task skill, automatic)
   ├─ Extract actions taken from work log
   ├─ Calculate duration and outcome
   ├─ Identify results and follow-ups
   ├─ Capture learnings
   └─ Append summary section to file

3. Update Metrics
   ├─ Increment completion counters
   ├─ Update Dashboard activity log
   └─ Calculate performance metrics
```

---

## Skill System Architecture

### Skill Structure

Every skill follows this template:

```markdown
# Skill: [Name]
- Purpose: What it does
- Trigger Condition: When it executes
- Input Format: Required data structure
- Output Format: Expected results
- Step-by-Step Reasoning: Deterministic pseudocode
- Success Criteria: Testable assertions
- Error Handling: Rollback procedures
```

### Available Skills

| Skill | Lines | Purpose | Trigger |
|-------|-------|---------|---------|
| triage_file | 286 | Assess and route tasks | New file in Inbox/ |
| summarize_task | 423 | Document completion | File moved to Done/ |
| move_to_folder | 422 | Safe file operations | Workflow transitions |

### Skill Execution Model

```
1. Input Validation
   └─ Verify all required parameters present and valid

2. State Verification
   └─ Check preconditions and system state

3. Execution
   ├─ Follow step-by-step reasoning exactly
   ├─ Log all actions
   └─ Handle errors per error handling section

4. Output Validation
   └─ Verify success criteria met

5. Audit Logging
   └─ Update Dashboard with action details
```

---

## Decision Framework

### Autonomous Decisions (No Escalation)

- Routine task execution following established patterns
- Formatting and presentation choices
- Tool selection for standard operations
- Scheduling non-critical work
- Documentation structure and detail level

### Escalation Required

- Decisions involving cost over $100
- Changes to core business logic or data models
- Security or privacy implications
- Ambiguous requirements with multiple valid interpretations
- Requests that conflict with handbook principles

### Escalation Process

```
1. Create task in Inbox/ with [ESCALATION] prefix
2. Include:
   ├─ Clear statement of blocker or question
   ├─ Relevant context
   ├─ 2-3 options with pros/cons
   ├─ Urgency level (P0-P3)
   └─ Current work status
3. Continue other work while waiting
4. Process response when received
```

---

## Priority System

| Level | Name | SLA | Use Case |
|-------|------|-----|----------|
| P0 | Critical | Immediate | System down, data loss, security breach |
| P1 | High | 4 hours | Blocking users, broken core features |
| P2 | Normal | 24 hours | Standard tasks, improvements |
| P3 | Low | 3 days | Nice-to-haves, documentation |

---

## Metadata Schema

### File Header (YAML Frontmatter)

```yaml
---
# Triage metadata
triaged_at: YYYY-MM-DD HH:MM
triaged_by: Digital FTE
status: needs_action|in_progress|completed|blocked
complexity: simple|moderate|complex
estimated_effort: 15min|1hr|4hr|1day|3day
sla_deadline: YYYY-MM-DD HH:MM

# Execution metadata
started_at: YYYY-MM-DD HH:MM
completed_at: YYYY-MM-DD HH:MM

# Move tracking
moved_at: YYYY-MM-DD HH:MM
moved_from: Inbox|Needs_Action|Done
moved_to: Inbox|Needs_Action|Done
moved_by: Digital FTE
move_reason: triage|started|completed|clarification|blocked

# Summary metadata
summarized_at: YYYY-MM-DD HH:MM
summarized_by: Digital FTE
---
```

---

## Performance Metrics

### Tracked in Dashboard

- **Tasks in Inbox:** Current count awaiting triage
- **Tasks Requiring Action:** Current count in Needs_Action/
- **Tasks Completed Today:** Daily completion counter
- **Total Tasks Completed:** Lifetime completion counter
- **Uptime:** System availability percentage

### Quality Metrics (Calculated from Done/)

- **Triage Time:** Time from creation to routing (target: <15min)
- **Completion Rate:** % of tasks reaching Done/ (target: >90%)
- **Clarification Rate:** % needing clarification (target: <20%)
- **Error Rate:** % of skill executions failing (target: <5%)
- **SLA Compliance:** % completed within SLA (target: >95%)

---

## File Naming Convention

```
YYYYMMDD-HHMM-task-description.md

Examples:
- 20260212-0915-fix-broken-documentation-link.md
- 20260212-1430-process-customer-feedback.md
- 20260213-0800-update-api-authentication.md
```

**Rules:**
- Date/time reflects task creation (not current time)
- Description is kebab-case (lowercase, hyphens)
- Keep description concise (3-7 words)
- Extension is always `.md`

---

## Error Handling Strategy

### Skill Execution Errors

```
1. Detect Error
   └─ Log error details to Dashboard

2. Attempt Rollback
   └─ Undo any partial changes

3. Preserve State
   └─ Keep files in current location

4. Notify
   └─ Create [ESCALATION] task if manual intervention needed

5. Continue
   └─ Process other tasks while waiting
```

### Data Integrity

- **Atomic operations:** All-or-nothing file moves
- **Verification:** Content checks before/after operations
- **Rollback:** Automatic cleanup on failure
- **Audit trail:** Complete history in metadata

---

## Extension Points

### Adding New Skills

1. Copy skill template structure
2. Define clear purpose and triggers
3. Write deterministic reasoning in pseudocode
4. Add comprehensive error handling
5. Include testable success criteria
6. Update SKILLS/README.md
7. Test with example tasks

### Adding New Folders

1. Create folder in AI_Employee_Vault/
2. Update move_to_folder.md with valid transitions
3. Update Dashboard.md with new metrics
4. Document purpose in this overview
5. Add to Company_Handbook.md workflow

### Custom Metadata Fields

1. Add field to metadata schema (above)
2. Update relevant skills to populate field
3. Document field purpose and format
4. Update Dashboard if field affects metrics

---

## Security Considerations

### Data Privacy

- All data stored locally (no external transmission)
- No API keys or credentials in task files
- Sensitive data should use placeholders
- Audit trail preserved for compliance

### Access Control

- File system permissions control access
- No authentication layer (local-first)
- Human operator has full control
- Digital FTE operates within defined boundaries

### Validation

- Input validation in every skill
- File format verification
- Metadata integrity checks
- Content sanitization where needed

---

## Troubleshooting

### Task Stuck in Inbox

**Symptoms:** File remains in Inbox/ beyond 15 minutes

**Possible Causes:**
- File has `[CLARIFICATION]` prefix → Add missing details
- File has `[BLOCKED]` prefix → Resolve dependencies
- Invalid file format → Check structure against template
- Triage skill failed → Check Dashboard for errors

**Resolution:**
1. Check Dashboard activity log for errors
2. Verify file format matches requirements
3. Add missing information if flagged
4. Manually move to Needs_Action/ if valid

### Task Not Completing

**Symptoms:** File stuck in Needs_Action/

**Possible Causes:**
- Acceptance criteria not checked off
- Work log missing or incomplete
- Actual blocker encountered
- Status not updated to "completed"

**Resolution:**
1. Review acceptance criteria
2. Check work log for blockers
3. Update status metadata
4. Manually move to Done/ if complete

### Summary Not Generated

**Symptoms:** File in Done/ lacks Summary section

**Possible Causes:**
- summarize_task skill didn't execute
- File moved manually (bypassed automation)
- Skill execution failed

**Resolution:**
1. Check Dashboard for skill execution errors
2. Manually invoke summarize_task skill
3. Add summary section manually if needed

---

## Best Practices

### For Task Creators

1. Use the standard task template
2. Include clear acceptance criteria (3-5 items)
3. Set realistic priority levels
4. Provide sufficient context
5. Specify due dates when relevant

### For Digital FTE Operators

1. Monitor Dashboard regularly
2. Process [ESCALATION] tasks promptly
3. Review Done/ folder for learnings
4. Update Company_Handbook.md as patterns emerge
5. Keep SKILLS/ documentation current

### For System Maintainers

1. Preserve deterministic skill logic
2. Test changes with example tasks
3. Update metadata schema carefully
4. Maintain backward compatibility
5. Document all architectural decisions

---

## Future Enhancements (Bronze → Silver)

Potential upgrades for higher tiers:

- **Automated scheduling:** Time-based task execution
- **Dependency management:** Task chains and prerequisites
- **Template library:** Common task templates
- **Metrics dashboard:** Visual analytics
- **Integration hooks:** External system connections
- **Multi-agent coordination:** Parallel task processing
- **Learning system:** Pattern recognition and optimization

---

## Version History

**1.0 (2026-02-12)**
- Initial Bronze Tier release
- Core folder structure
- 3 foundational skills
- Company Handbook and Dashboard
- Complete workflow automation
- Deterministic execution model

---

## Support & Documentation

- **Company_Handbook.md:** Operating rules and decision framework
- **SKILLS/README.md:** Skill system documentation
- **Dashboard.md:** Current system status
- **This file:** Architecture and design decisions

For questions or issues, create an [ESCALATION] task in Inbox/.

---

**Remember:** This is a Bronze Tier system focused on deterministic, local-first automation. Every component is designed to be human-readable, auditable, and maintainable without specialized tools.
