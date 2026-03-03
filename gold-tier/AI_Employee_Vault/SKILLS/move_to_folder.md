# Skill: Move to Folder

**Version:** 1.0
**Type:** Workflow Management
**Execution Mode:** Manual or Automatic

---

## Purpose

Safely move task files between workflow folders (Inbox, Needs_Action, Done) with validation, state tracking, and audit logging.

---

## Trigger Condition

Execute when ANY of these conditions are met:
- Task status changes require folder relocation
- Manual invocation with source file and destination folder
- Automated workflow transition (triage → action, action → completion)

---

## Input Format

**Required Parameters:**

```json
{
  "source_file": "path/to/file.md",
  "destination_folder": "Inbox|Needs_Action|Done",
  "reason": "triage|started|completed|clarification|blocked",
  "preserve_metadata": true|false
}
```

**Valid Folder Transitions:**
```
Inbox → Needs_Action  (reason: triage, started)
Inbox → Inbox         (reason: clarification, blocked - with prefix)
Needs_Action → Done   (reason: completed)
Needs_Action → Inbox  (reason: clarification, blocked)
Done → Needs_Action   (reason: reopened - requires approval)
```

---

## Output Format

**Action 1:** Update file metadata before move:

```markdown
---
moved_at: YYYY-MM-DD HH:MM
moved_from: [source_folder]
moved_to: [destination_folder]
moved_by: Digital FTE
move_reason: [reason]
previous_location: [full_path]
---
```

**Action 2:** Execute file move operation

**Action 3:** Log move in Dashboard activity log

**Return Value:**
```json
{
  "success": true|false,
  "old_path": "original/path/file.md",
  "new_path": "destination/path/file.md",
  "timestamp": "YYYY-MM-DD HH:MM",
  "error": null|"error message"
}
```

---

## Step-by-Step Reasoning Process

### Step 1: Validate Input Parameters
```
IF source_file is NULL OR source_file is empty THEN
  RETURN error("Source file path is required")
END IF

IF destination_folder is NULL OR destination_folder is empty THEN
  RETURN error("Destination folder is required")
END IF

valid_folders = ["Inbox", "Needs_Action", "Done"]
IF destination_folder NOT IN valid_folders THEN
  RETURN error("Invalid destination folder: " + destination_folder)
END IF

valid_reasons = ["triage", "started", "completed", "clarification", "blocked", "reopened"]
IF reason NOT IN valid_reasons THEN
  RETURN error("Invalid move reason: " + reason)
END IF
```

### Step 2: Verify Source File Exists
```
IF NOT file_exists(source_file) THEN
  RETURN error("Source file does not exist: " + source_file)
END IF

IF NOT is_markdown_file(source_file) THEN
  RETURN error("Source file must be a .md file: " + source_file)
END IF

source_folder = extract_folder_name(source_file)
source_filename = extract_filename(source_file)
```

### Step 3: Validate Transition Rules
```
transition_key = source_folder + " → " + destination_folder

valid_transitions = {
  "Inbox → Needs_Action": ["triage", "started"],
  "Inbox → Inbox": ["clarification", "blocked"],
  "Needs_Action → Done": ["completed"],
  "Needs_Action → Inbox": ["clarification", "blocked"],
  "Done → Needs_Action": ["reopened"]
}

IF transition_key NOT IN valid_transitions THEN
  RETURN error("Invalid transition: " + transition_key)
END IF

allowed_reasons = valid_transitions[transition_key]
IF reason NOT IN allowed_reasons THEN
  RETURN error("Reason '" + reason + "' not allowed for transition " + transition_key)
END IF
```

### Step 4: Handle Special Cases
```
# Special case: Moving within same folder (Inbox → Inbox)
IF source_folder == destination_folder AND destination_folder == "Inbox" THEN
  # This is a rename operation with prefix
  IF reason == "clarification" THEN
    prefix = "[CLARIFICATION]-"
  ELSE IF reason == "blocked" THEN
    prefix = "[BLOCKED]-"
  ELSE
    RETURN error("Same-folder move requires clarification or blocked reason")
  END IF

  # Check if file already has prefix
  IF source_filename starts_with prefix THEN
    log_info("File already has prefix, skipping rename", source_filename)
    RETURN success(source_file, source_file)
  END IF

  new_filename = prefix + source_filename
  destination_path = "Inbox/" + new_filename
  is_rename_operation = TRUE
ELSE
  destination_path = destination_folder + "/" + source_filename
  is_rename_operation = FALSE
END IF
```

### Step 5: Check Destination Conflicts
```
IF file_exists(destination_path) THEN
  # Generate unique filename with timestamp
  timestamp_suffix = format_timestamp("_YYYYMMDD-HHMM")
  filename_without_ext = remove_extension(source_filename)
  file_extension = get_extension(source_filename)

  new_filename = filename_without_ext + timestamp_suffix + file_extension
  destination_path = destination_folder + "/" + new_filename

  log_warning("Destination file exists, using unique name", new_filename)

  # Verify new path doesn't exist
  IF file_exists(destination_path) THEN
    RETURN error("Unable to generate unique filename after conflict")
  END IF
END IF
```

### Step 6: Read and Update Metadata
```
IF preserve_metadata == TRUE THEN
  file_content = read_file(source_file)

  # Extract existing metadata if present
  IF file_content starts_with "---" THEN
    metadata_end = find_second_occurrence(file_content, "---")
    existing_metadata = extract_yaml(file_content, 0, metadata_end)
    content_body = file_content[metadata_end:]
  ELSE
    existing_metadata = {}
    content_body = file_content
  END IF

  # Add move tracking metadata
  move_metadata = {
    moved_at: current_timestamp(),
    moved_from: source_folder,
    moved_to: destination_folder,
    moved_by: "Digital FTE",
    move_reason: reason,
    previous_location: source_file
  }

  # Merge metadata
  updated_metadata = merge_yaml(existing_metadata, move_metadata)

  # Reconstruct file content
  updated_content = format_yaml_frontmatter(updated_metadata) + content_body
ELSE
  updated_content = read_file(source_file)
END IF
```

### Step 7: Execute Move Operation
```
TRY:
  # Create destination folder if it doesn't exist
  IF NOT folder_exists(destination_folder) THEN
    create_folder(destination_folder)
    log_info("Created destination folder", destination_folder)
  END IF

  # Write file to destination with updated metadata
  write_file(destination_path, updated_content)

  # Verify write was successful
  IF NOT file_exists(destination_path) THEN
    THROW error("File write verification failed")
  END IF

  # Verify content integrity
  written_content = read_file(destination_path)
  IF written_content != updated_content THEN
    THROW error("Content integrity check failed")
  END IF

  # Delete source file
  delete_file(source_file)

  # Verify deletion
  IF file_exists(source_file) THEN
    THROW error("Source file deletion failed")
  END IF

  move_success = TRUE

CATCH error:
  log_error("Move operation failed", error.message)

  # Rollback: delete destination if it was created
  IF file_exists(destination_path) THEN
    delete_file(destination_path)
  END IF

  move_success = FALSE
  error_message = error.message
END TRY
```

### Step 8: Update Dashboard
```
IF move_success == TRUE THEN
  dashboard_path = "Dashboard.md"

  # Format activity log entry
  activity_entry = format_log_entry({
    timestamp: current_timestamp(),
    action: "Moved file",
    file: source_filename,
    from: source_folder,
    to: destination_folder,
    reason: reason
  })

  append_to_activity_log(dashboard_path, activity_entry)

  # Update folder metrics
  IF destination_folder == "Needs_Action" THEN
    increment_dashboard_metric("Tasks Requiring Action")
  ELSE IF destination_folder == "Done" THEN
    increment_dashboard_metric("Tasks Completed Today")
    decrement_dashboard_metric("Tasks Requiring Action")
  END IF
END IF
```

### Step 9: Return Result
```
IF move_success == TRUE THEN
  RETURN {
    success: TRUE,
    old_path: source_file,
    new_path: destination_path,
    timestamp: current_timestamp(),
    error: NULL
  }
ELSE
  RETURN {
    success: FALSE,
    old_path: source_file,
    new_path: NULL,
    timestamp: current_timestamp(),
    error: error_message
  }
END IF
```

---

## Success Criteria

**Must ALL be TRUE:**
- [ ] Source file no longer exists at original location
- [ ] Destination file exists at new location
- [ ] File content is identical (except metadata)
- [ ] Metadata has been updated with move tracking
- [ ] Dashboard activity log has been updated
- [ ] No orphaned files in any folder
- [ ] Folder metrics are accurate

**Validation Checks:**
```
ASSERT NOT file_exists(source_file)
ASSERT file_exists(destination_path)
ASSERT file_contains(destination_path, "moved_at:")
ASSERT file_contains(destination_path, "moved_from: " + source_folder)
ASSERT file_contains(destination_path, "moved_to: " + destination_folder)
ASSERT dashboard_contains_entry(source_filename, "Moved file")
```

---

## Error Handling

**If source file does not exist:**
```
log_error("Source file not found", source_file)
RETURN error("Cannot move non-existent file: " + source_file)
```

**If destination folder is invalid:**
```
log_error("Invalid destination folder", destination_folder)
RETURN error("Destination must be one of: Inbox, Needs_Action, Done")
```

**If transition is not allowed:**
```
log_error("Invalid transition", source_folder + " → " + destination_folder)
RETURN error("Transition not allowed per workflow rules")
```

**If file write fails:**
```
log_error("Unable to write destination file", destination_path)
rollback_operation()
RETURN error("File write failed - operation rolled back")
```

**If source deletion fails:**
```
log_error("Unable to delete source file", source_file)
# Destination file exists, source file exists - manual intervention needed
notify_escalation("Move operation incomplete - duplicate files exist")
RETURN error("Source deletion failed - manual cleanup required")
```

**If metadata update fails:**
```
log_warning("Metadata update failed, proceeding with move", source_file)
# Continue with move operation using original content
preserve_metadata = FALSE
RETRY move operation
```

---

## Atomic Operation Guarantee

This skill implements atomic move operations:

1. **Write-then-delete pattern:** Destination is written first, source deleted only after verification
2. **Rollback on failure:** Any failure triggers cleanup of partial operations
3. **Integrity checks:** Content verification before source deletion
4. **Idempotent:** Can be safely retried if interrupted

**Transaction Log:**
```
BEGIN TRANSACTION
  WRITE destination_file
  VERIFY destination_file
  DELETE source_file
  VERIFY source_deleted
  UPDATE dashboard
COMMIT TRANSACTION

ON ERROR:
  ROLLBACK TRANSACTION
  DELETE destination_file (if exists)
  PRESERVE source_file
  LOG error
END
```

---

## Notes

- This skill is the foundation for all workflow transitions
- All file movements must go through this skill for audit compliance
- Metadata preservation ensures complete audit trail
- Atomic operations prevent data loss during moves
- Dashboard metrics stay synchronized with actual folder state
- Special handling for same-folder renames (clarification/blocked flags)
