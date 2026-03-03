# Skill: Summarize Task

**Version:** 1.0
**Type:** Documentation
**Execution Mode:** Automatic on completion

---

## Purpose

Generate a structured summary of completed task outcomes, actions taken, and follow-up items for audit trail and knowledge capture.

---

## Trigger Condition

Execute when ANY of these conditions are met:
- File is moved from `Needs_Action/` to `Done/` folder
- File in `Done/` lacks a `## Summary` section
- Manual invocation with file path parameter

---

## Input Format

**Required:** Markdown file with task execution history:

```markdown
---
triaged_at: YYYY-MM-DD HH:MM
status: completed
started_at: YYYY-MM-DD HH:MM
completed_at: YYYY-MM-DD HH:MM
---

# [Task Title]

**Priority:** [P0|P1|P2|P3]

## Description
[Original task description]

## Work Log
[Timestamped entries of actions taken]

## Acceptance Criteria
- [x] Completed criterion 1
- [x] Completed criterion 2
```

**Minimum Required Fields:**
- Task Title
- Work Log or execution history
- Completion timestamp in metadata

---

## Output Format

**Action:** Append summary section to file:

```markdown
---
## Summary

**Completed:** YYYY-MM-DD HH:MM
**Duration:** [Xh Ym]
**Outcome:** [Success|Partial|Blocked]

### Actions Taken
- Action 1 with specific details
- Action 2 with specific details
- Action 3 with specific details

### Results
- Measurable outcome 1
- Measurable outcome 2

### Follow-ups
- [ ] Follow-up task 1 (if any)
- [ ] Follow-up task 2 (if any)

### Learnings
- Key insight or pattern identified (if applicable)

---
```

---

## Step-by-Step Reasoning Process

### Step 1: Extract Metadata
```
READ file_metadata
extract_fields = {
  started_at: metadata.started_at,
  completed_at: metadata.completed_at,
  priority: metadata.priority,
  complexity: metadata.complexity
}

IF completed_at is NULL THEN
  completed_at = current_timestamp()
END IF

IF started_at is NULL THEN
  started_at = triaged_at
END IF

duration = calculate_duration(started_at, completed_at)
```

### Step 2: Parse Work Log
```
work_log_section = extract_section("## Work Log")

IF work_log_section is NULL THEN
  work_log_section = extract_section("## Progress")
END IF

IF work_log_section is NULL THEN
  actions_taken = ["Task completed (no detailed log available)"]
  GOTO Step 4
END IF

actions_taken = []
FOR EACH line IN work_log_section:
  IF line starts_with("- ") OR line starts_with("* ") OR line matches timestamp_pattern THEN
    action = clean_action_text(line)
    actions_taken.append(action)
  END IF
END FOR

IF length(actions_taken) == 0 THEN
  actions_taken = ["Task completed per requirements"]
END IF
```

### Step 3: Assess Outcome
```
acceptance_criteria_section = extract_section("## Acceptance Criteria")

IF acceptance_criteria_section exists THEN
  total_criteria = count_checkboxes(acceptance_criteria_section)
  completed_criteria = count_checked_checkboxes(acceptance_criteria_section)

  completion_rate = completed_criteria / total_criteria

  IF completion_rate == 1.0 THEN
    outcome = "Success"
  ELSE IF completion_rate >= 0.7 THEN
    outcome = "Partial"
  ELSE
    outcome = "Blocked"
  END IF
ELSE
  # No explicit criteria - check for blocker keywords
  IF file_content contains "blocked" OR "unable to" OR "failed" THEN
    outcome = "Blocked"
  ELSE
    outcome = "Success"
  END IF
END IF
```

### Step 4: Extract Results
```
results = []

# Look for explicit results section
results_section = extract_section("## Results")
IF results_section exists THEN
  FOR EACH line IN results_section:
    IF line starts_with("- ") OR line starts_with("* ") THEN
      results.append(clean_text(line))
    END IF
  END FOR
END IF

# If no explicit results, infer from acceptance criteria
IF length(results) == 0 AND acceptance_criteria_section exists THEN
  FOR EACH checked_item IN acceptance_criteria_section:
    IF checkbox_is_checked(checked_item) THEN
      result = convert_criteria_to_result(checked_item)
      results.append(result)
    END IF
  END FOR
END IF

# Default if nothing found
IF length(results) == 0 THEN
  results = ["Task requirements met per specification"]
END IF
```

### Step 5: Identify Follow-ups
```
followups = []

# Check for explicit follow-up section
followup_section = extract_section("## Follow-up") OR extract_section("## Next Steps")
IF followup_section exists THEN
  FOR EACH line IN followup_section:
    IF line starts_with("- [ ]") OR line starts_with("* [ ]") THEN
      followups.append(clean_text(line))
    END IF
  END FOR
END IF

# Look for follow-up keywords in work log
followup_keywords = ["TODO:", "Next:", "Follow-up:", "Need to:"]
FOR EACH line IN work_log_section:
  FOR EACH keyword IN followup_keywords:
    IF line contains keyword THEN
      followup = extract_after_keyword(line, keyword)
      followups.append("[ ] " + followup)
    END IF
  END FOR
END FOR

# Check if outcome is Partial or Blocked
IF outcome == "Partial" OR outcome == "Blocked" THEN
  uncompleted = get_unchecked_criteria(acceptance_criteria_section)
  FOR EACH item IN uncompleted:
    followups.append("[ ] Complete: " + item)
  END FOR
END IF
```

### Step 6: Capture Learnings
```
learnings = []

# Look for explicit learnings section
learning_section = extract_section("## Learnings") OR extract_section("## Notes")
IF learning_section exists THEN
  FOR EACH line IN learning_section:
    IF line starts_with("- ") OR line starts_with("* ") THEN
      learnings.append(clean_text(line))
    END IF
  END FOR
END IF

# Check for error patterns or insights
IF work_log_section contains "error" OR "issue" OR "problem" THEN
  error_lines = extract_lines_with_keywords(work_log_section, ["error", "issue", "problem", "solved"])
  FOR EACH line IN error_lines:
    IF line contains "solved" OR "fixed" OR "resolved" THEN
      learning = extract_learning_from_resolution(line)
      IF learning is not NULL THEN
        learnings.append(learning)
      END IF
    END IF
  END FOR
END IF
```

### Step 7: Format Summary
```
summary_template = """
---
## Summary

**Completed:** {completed_at}
**Duration:** {duration}
**Outcome:** {outcome}

### Actions Taken
{actions_list}

### Results
{results_list}

{followups_section}

{learnings_section}

---
"""

# Build actions list
actions_list = ""
FOR EACH action IN actions_taken:
  actions_list += "- " + action + "\n"
END FOR

# Build results list
results_list = ""
FOR EACH result IN results:
  results_list += "- " + result + "\n"
END FOR

# Build follow-ups section (only if exists)
followups_section = ""
IF length(followups) > 0 THEN
  followups_section = "### Follow-ups\n"
  FOR EACH followup IN followups:
    followups_section += "- " + followup + "\n"
  END FOR
END IF

# Build learnings section (only if exists)
learnings_section = ""
IF length(learnings) > 0 THEN
  learnings_section = "### Learnings\n"
  FOR EACH learning IN learnings:
    learnings_section += "- " + learning + "\n"
  END FOR
END IF

summary_content = format(summary_template, {
  completed_at: completed_at,
  duration: duration,
  outcome: outcome,
  actions_list: actions_list,
  results_list: results_list,
  followups_section: followups_section,
  learnings_section: learnings_section
})
```

### Step 8: Append Summary
```
file_content = read_file(file_path)

# Check if summary already exists
IF file_content contains "## Summary" THEN
  log_warning("Summary already exists", file_path)
  RETURN
END IF

# Append summary to end of file
append_to_file(file_path, summary_content)

# Update metadata
update_metadata(file_path, {
  summarized_at: current_timestamp(),
  summarized_by: "Digital FTE"
})
```

### Step 9: Update Dashboard
```
dashboard_path = "Dashboard.md"
activity_entry = format_log_entry({
  timestamp: current_timestamp(),
  action: "Summarized completed task",
  file: get_filename(file_path),
  outcome: outcome,
  duration: duration
})

append_to_activity_log(dashboard_path, activity_entry)

# Update completion metrics
increment_dashboard_metric("Tasks Completed Today")
increment_dashboard_metric("Total Tasks Completed")
```

---

## Success Criteria

**Must ALL be TRUE:**
- [ ] Summary section has been appended to file
- [ ] Summary contains all required subsections (Actions, Results)
- [ ] Outcome is accurately determined (Success/Partial/Blocked)
- [ ] Duration is calculated correctly
- [ ] Follow-ups are identified (if any exist)
- [ ] Dashboard metrics are updated
- [ ] No duplicate summary sections exist in file

**Validation Checks:**
```
ASSERT file_contains(file_path, "## Summary")
ASSERT file_contains(file_path, "### Actions Taken")
ASSERT file_contains(file_path, "### Results")
ASSERT outcome IN ["Success", "Partial", "Blocked"]
ASSERT duration matches format "[0-9]+h [0-9]+m" OR "[0-9]+m"
ASSERT count_sections(file_path, "## Summary") == 1
```

---

## Error Handling

**If file cannot be read:**
```
log_error("Unable to read file for summarization", file_path)
notify_escalation("Summary generation failed - manual review required")
RETURN
```

**If work log is empty:**
```
log_warning("No work log found", file_path)
actions_taken = ["Task completed (no detailed log available)"]
CONTINUE with summary generation
```

**If summary already exists:**
```
log_info("Summary already exists, skipping", file_path)
RETURN without error
```

**If file write fails:**
```
log_error("Unable to write summary", file_path)
save_summary_to_temp_file(summary_content, file_path + ".summary.tmp")
notify_escalation("Summary saved to temp file - manual merge required")
```

---

## Notes

- This skill executes automatically when tasks are completed
- Summary provides audit trail for all completed work
- Follow-ups can be extracted and converted to new tasks
- Learnings feed into continuous improvement process
- Duration tracking helps refine effort estimates
