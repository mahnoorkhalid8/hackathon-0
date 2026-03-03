---
id: 002
title: SKILLS System Creation
stage: general
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: SEVEN86 COMPUTES
command: none
labels: ["skills", "automation", "deterministic-agents", "workflow"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - AI_Employee_Vault/SKILLS/triage_file.md
  - AI_Employee_Vault/SKILLS/summarize_task.md
  - AI_Employee_Vault/SKILLS/move_to_folder.md
tests: []
---

## Prompt

You are building structured Agent Skills for a Digital FTE.

Create a SKILLS system where each skill is a Markdown file.

Requirements:

1. Create folder:
   AI_Employee_Vault/SKILLS/

2. Create 3 skills:
   - triage_file.md
   - summarize_task.md
   - move_to_folder.md

3. Each skill must include:
   - Skill Name
   - Purpose
   - Trigger condition
   - Input format
   - Output format
   - Step-by-step reasoning process
   - Success criteria

This must follow a deterministic agent pattern (no vague instructions).

Return the complete Markdown contents for each skill.

## Response

Created a complete deterministic SKILLS system with three production-ready skill files:

**1. triage_file.md (286 lines)**
- Purpose: Assess and route incoming tasks from Inbox
- Trigger: New .md file in Inbox/ (automatic within 15 minutes)
- 8-step reasoning process with explicit pseudocode
- Validates structure, assesses priority/complexity, detects blockers
- Routes to Needs_Action or flags for clarification/blocked
- Updates Dashboard activity log and metrics

**2. summarize_task.md (423 lines)**
- Purpose: Generate structured summaries of completed tasks
- Trigger: File moved to Done/ folder (automatic)
- 9-step reasoning process for extracting outcomes
- Parses work logs, calculates duration, assesses completion rate
- Identifies follow-ups and captures learnings
- Determines outcome (Success/Partial/Blocked)

**3. move_to_folder.md (422 lines)**
- Purpose: Safely move files between workflow folders with audit trail
- Trigger: Manual or automatic workflow transitions
- 9-step atomic operation with rollback capability
- Validates transition rules (Inbox→Needs_Action→Done)
- Implements write-then-delete pattern for data safety
- Updates metadata and Dashboard metrics

**Deterministic Design Principles:**
- Every step is explicit pseudocode (IF/THEN/FOR/WHILE)
- No ambiguous instructions or vague language
- Comprehensive error handling with specific rollback procedures
- Validation checks at every step
- Testable success criteria with assertions
- Complete audit trail through metadata tracking

All skills are executable by any agent following the step-by-step reasoning without interpretation or guesswork.

## Outcome

✓ SKILLS folder created
✓ Three deterministic skill files (1,131 total lines)
✓ Complete with input/output formats, reasoning processes, success criteria
✓ Production-ready for Bronze Tier Digital FTE automation
