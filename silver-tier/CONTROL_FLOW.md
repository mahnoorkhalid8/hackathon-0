# Silver Tier Digital FTE - Control Flow Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SILVER TIER DIGITAL FTE                      │
│                     Local-First Autonomous Assistant                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Control Flow

```
                    ┌─────────────────────────┐
                    │   SYSTEM STARTUP        │
                    │   main.py               │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Initialize            │
                    │   Orchestrator          │
                    │   - Load config         │
                    │   - Create components   │
                    │   - Setup event queue   │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ File Watcher │ │ Time Watcher │ │ Other        │
    │              │ │              │ │ Watchers     │
    │ Monitors:    │ │ Checks:      │ │              │
    │ - Inbox/     │ │ - Schedule   │ │ - Email      │
    │ - *.md files │ │ - Intervals  │ │ - Webhooks   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   EVENT DETECTED              │
            │   - File created              │
            │   - Time reached              │
            │   - External trigger          │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   ORCHESTRATOR                │
            │   Event Queue                 │
            │   - Deduplicate               │
            │   - Prioritize                │
            │   - Queue for processing      │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   CONTEXT LOADER              │
            │   Load from Memory Vault:     │
            │   ✓ Dashboard.md              │
            │   ✓ Company_Handbook.md       │
            │   ✓ Plan.md                   │
            │   ✓ Matched Skill             │
            │   ✓ Event Details             │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   REASONING ENGINE            │
            │   Iterative Analysis:         │
            │   1. Describe situation       │
            │   2. Extract policies         │
            │   3. Analyze skill            │
            │   4. Generate steps           │
            │   5. Make decision            │
            │   6. Calculate confidence     │
            │   7. Update Plan.md           │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   TASK ROUTER                 │
            │   Decision Logic:             │
            │   - Check approval rules      │
            │   - Evaluate confidence       │
            │   - Assess risk level         │
            │   - Apply safety defaults     │
            └───────────────┬───────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  Needs_Action/      │         │  Needs_Approval/    │
│  (Auto-Execute)     │         │  (Human Review)     │
│                     │         │                     │
│  Conditions:        │         │  Conditions:        │
│  • High confidence  │         │  • Low confidence   │
│  • Known skill      │         │  • Unknown pattern  │
│  • Low risk         │         │  • High risk        │
│  • Pre-approved     │         │  • MCP required     │
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           │                               ▼
           │                    ┌─────────────────────┐
           │                    │  HUMAN REVIEWS      │
           │                    │  - Read task file   │
           │                    │  - Check reasoning  │
           │                    │  - Make decision    │
           │                    │  - Add approval     │
           │                    └──────────┬──────────┘
           │                               │
           │                    ┌──────────┴──────────┐
           │                    │                     │
           │                    ▼                     ▼
           │         ┌─────────────────┐   ┌─────────────────┐
           │         │   APPROVED      │   │   REJECTED      │
           │         │   Move to       │   │   Archive &     │
           │         │   Needs_Action/ │   │   Log reason    │
           │         └────────┬────────┘   └─────────────────┘
           │                  │
           └──────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   EXECUTOR                │
        │   Task Execution:         │
        │   1. Parse task file      │
        │   2. Load skill def       │
        │   3. Execute steps        │
        │   4. Call MCP if needed   │
        │   5. Handle errors        │
        │   6. Capture results      │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   MCP CLIENT              │
        │   (If Required)           │
        │   - External API call     │
        │   - Web search            │
        │   - Data fetch            │
        │   - Log all calls         │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   STATE MANAGER           │
        │   Finalization:           │
        │   ✓ Update Dashboard.md   │
        │   ✓ Move to Done/         │
        │   ✓ Add to activity log   │
        │   ✓ Update metrics        │
        │   ✓ Log completion        │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   DONE/                   │
        │   Archived by month       │
        │   - Complete audit trail  │
        │   - Execution results     │
        │   - Timestamps            │
        └───────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   LOOP CONTINUES          │
        │   Return to monitoring    │
        │   Wait for next event     │
        └───────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│ Event        │
│ {            │
│   type       │──┐
│   source     │  │
│   timestamp  │  │
│   payload    │  │
│ }            │  │
└──────────────┘  │
                  │
                  ▼
┌──────────────────────────────┐
│ Context                      │
│ {                            │
│   event: {...}               │
│   dashboard: "..."           │
│   handbook: "..."            │
│   plan: "..."                │
│   skill_definition: "..."    │
│   matched_skill: "name"      │
│ }                            │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Reasoning                    │
│ {                            │
│   situation: "..."           │
│   analysis: [...]            │
│   decision: {                │
│     action: "..."            │
│     reason: "..."            │
│   }                          │
│   confidence: 85             │
│   requires_approval: false   │
│ }                            │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Task File (Markdown)         │
│ - Event details              │
│ - Reasoning summary          │
│ - Decision                   │
│ - Approval section           │
│ - Execution log              │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Execution Result             │
│ {                            │
│   status: "success"          │
│   message: "..."             │
│   outputs: {...}             │
│   duration: "2.5s"           │
│ }                            │
└──────────────────────────────┘
```

## State Transitions

```
Event States:
  NEW → QUEUED → PROCESSING → ROUTED → [APPROVED] → EXECUTING → COMPLETED

Task States:
  PENDING → IN_PROGRESS → COMPLETED
                       → FAILED → REQUIRES_APPROVAL

Approval States:
  NEEDS_REVIEW → APPROVED → NEEDS_ACTION
              → REJECTED → ARCHIVED
              → MODIFIED → NEEDS_ACTION
```

## Error Handling Flow

```
┌─────────────┐
│ Error       │
│ Detected    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Error Type?     │
└──────┬──────────┘
       │
       ├─→ Transient → Retry (max 2x) → Success/Fail
       │
       ├─→ Configuration → Log + Alert Human
       │
       ├─→ Skill Error → Move to Needs_Approval
       │
       └─→ Critical → Stop + Alert + Log
```

## Concurrency Model

```
Main Thread:
  - Orchestrator control loop
  - Event queue management
  - Component coordination

Worker Threads:
  - File Watcher (watchdog observer)
  - Time Watcher (schedule checker)
  - Event Processor (queue consumer)
  - Task Executor (action processor)

Thread Safety:
  - Event queue (thread-safe)
  - File operations (atomic writes)
  - Metrics (lock-protected)
```

---

*This diagram represents the complete control flow of the Silver Tier Digital FTE system.*
