# Skill: Triage File

**Version:** 1.0
**Type:** Intake Processing
**Execution Mode:** Automatic

---

## Purpose

Assess incoming task files in the Inbox and route them to the appropriate workflow stage based on priority, completeness, and actionability.

---

## Trigger Condition

Execute when ANY of these conditions are met:
- New `.md` file detected in `Inbox/` folder
- File timestamp in `Inbox/` is less than 15 minutes old
- Manual invocation with file path parameter

---

## Input Format

**Required:** Markdown file in `Inbox/` with the following structure:

```markdown
# [Task Title]

**Priority:** [P0|P1|P2|P3]
**Requester:** [Name or System]
**Due Date:** [YYYY-MM-DD or "None"]

## Description
[Task details and requirements]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Context
[Optional: Background information]
```

**Minimum Required Fields:**
- Task Title (H1 heading)
- Priority level
- Description section

---

## Output Format

**Action 1:** Add triage metadata to file header:

```markdown
---
triaged_at: YYYY-MM-DD HH:MM
triaged_by: Digital FTE
status: [needs_action|needs_clarification|blocked]
complexity: [simple|moderate|complex]
estimated_effort: [15min|1hr|4hr|1day|3day]
---
```

**Action 2:** Move file to destination:
- `Needs_Action/` if actionable
- `Inbox/[CLARIFICATION]-original-filename.md` if underspecified
- `Inbox/[BLOCKED]-original-filename.md` if dependencies exist

**Action 3:** Update Dashboard activity log

---

## Step-by-Step Reasoning Process

### Step 1: Validate File Structure
```
IF file has H1 heading THEN
  extract_title = TRUE
ELSE
  flag_for_clarification = TRUE
  GOTO Step 7
END IF

IF file contains "Priority:" field THEN
  extract_priority = TRUE
ELSE
  default_priority = "P2"
END IF

IF file contains "Description" section THEN
  extract_description = TRUE
ELSE
  flag_for_clarification = TRUE
  GOTO Step 7
END IF
```

### Step 2: Assess Priority Level
```
READ priority_field
MATCH priority_field:
  CASE "P0": urgency = "critical", sla = "immediate"
  CASE "P1": urgency = "high", sla = "4 hours"
  CASE "P2": urgency = "normal", sla = "24 hours"
  CASE "P3": urgency = "low", sla = "3 days"
  DEFAULT: urgency = "normal", sla = "24 hours"
END MATCH
```

### Step 3: Evaluate Completeness
```
completeness_score = 0

IF title exists AND title length > 5 characters THEN
  completeness_score += 25
END IF

IF description exists AND description length > 20 characters THEN
  completeness_score += 25
END IF

IF acceptance_criteria exists AND has at least 1 checkbox THEN
  completeness_score += 25
END IF

IF priority is explicitly set THEN
  completeness_score += 25
END IF

IF completeness_score < 50 THEN
  status = "needs_clarification"
  GOTO Step 7
ELSE
  status = "needs_action"
END IF
```

### Step 4: Assess Complexity
```
complexity_indicators = []

IF description contains "integrate" OR "API" OR "database" THEN
  complexity_indicators.append("technical")
END IF

IF description contains "multiple" OR "several" OR "various" THEN
  complexity_indicators.append("scope")
END IF

IF acceptance_criteria count > 5 THEN
  complexity_indicators.append("detailed")
END IF

IF length(complexity_indicators) == 0 THEN
  complexity = "simple"
  estimated_effort = "15min"
ELSE IF length(complexity_indicators) == 1 THEN
  complexity = "moderate"
  estimated_effort = "1hr"
ELSE
  complexity = "complex"
  estimated_effort = "4hr"
END IF
```

### Step 5: Check for Blockers
```
blocker_keywords = ["waiting for", "depends on", "blocked by", "need approval"]
description_lower = description.to_lowercase()

FOR EACH keyword IN blocker_keywords:
  IF description_lower contains keyword THEN
    status = "blocked"
    GOTO Step 7
  END IF
END FOR
```

### Step 6: Add Metadata
```
current_timestamp = get_current_datetime()
metadata_block = format_yaml({
  triaged_at: current_timestamp,
  triaged_by: "Digital FTE",
  status: status,
  complexity: complexity,
  estimated_effort: estimated_effort,
  sla_deadline: calculate_deadline(current_timestamp, sla)
})

prepend_to_file(metadata_block)
```

### Step 7: Route File
```
original_filename = get_filename()
original_path = "Inbox/" + original_filename

IF status == "needs_action" THEN
  destination = "Needs_Action/" + original_filename
  move_file(original_path, destination)
  log_action("Triaged and moved to Needs_Action", original_filename)

ELSE IF status == "needs_clarification" THEN
  new_filename = "[CLARIFICATION]-" + original_filename
  destination = "Inbox/" + new_filename
  rename_file(original_path, destination)
  log_action("Flagged for clarification", new_filename)

ELSE IF status == "blocked" THEN
  new_filename = "[BLOCKED]-" + original_filename
  destination = "Inbox/" + new_filename
  rename_file(original_path, destination)
  log_action("Flagged as blocked", new_filename)
END IF
```

### Step 8: Update Dashboard
```
dashboard_path = "Dashboard.md"
activity_entry = format_log_entry({
  timestamp: current_timestamp,
  action: "Triaged task",
  file: original_filename,
  status: status,
  priority: priority
})

append_to_activity_log(dashboard_path, activity_entry)
```

---

## Success Criteria

**Must ALL be TRUE:**
- [ ] File has been read successfully
- [ ] Metadata block has been added to file
- [ ] File has been moved or renamed based on status
- [ ] Dashboard activity log has been updated
- [ ] No files remain in `Inbox/` without `[CLARIFICATION]` or `[BLOCKED]` prefix
- [ ] Triage completed within 15 minutes of file creation

**Validation Checks:**
```
ASSERT file_exists(destination_path)
ASSERT NOT file_exists(original_path) OR original_path contains "[CLARIFICATION]" OR "[BLOCKED]"
ASSERT metadata_block in file_content
ASSERT dashboard_updated == TRUE
```

---

## Error Handling

**If file is corrupted or unreadable:**
```
rename_file(original_path, "Inbox/[ERROR]-" + original_filename)
log_error("Unable to read file", original_filename)
notify_escalation("File triage failed - manual review required")
```

**If destination folder does not exist:**
```
create_folder(destination)
retry_move_operation()
```

**If metadata cannot be added:**
```
log_warning("Metadata addition failed", original_filename)
proceed_with_move_operation()
note_in_dashboard("Triaged without metadata - manual review recommended")
```

---

## Notes

- This skill executes automatically on new files
- Triage must complete within 15 minutes per Company Handbook SLA
- Files flagged for clarification remain in Inbox with prefix
- Blocked files remain in Inbox until blocker is resolved
