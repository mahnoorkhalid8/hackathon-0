# Silver Tier Digital FTE - Architecture Document

## Executive Summary

The Silver Tier Digital FTE is a local-first autonomous digital employee that uses markdown-based memory, multi-watcher triggers, iterative reasoning loops, and human-in-the-loop approval for safe autonomous operation.

## Design Philosophy

### Core Principles

1. **Local-First**: All state stored in git-trackable markdown files
2. **Safety-First**: Default to human approval for uncertain operations
3. **Transparency**: All reasoning documented and auditable
4. **Modularity**: Pluggable watchers, skills, and MCP integrations
5. **Human-in-the-Loop**: Critical decisions require human approval

### Key Differentiators

- **Markdown Memory Vault**: Human-readable, git-trackable state
- **Iterative Reasoning**: Plan.md shows step-by-step thinking
- **Approval Queues**: Separate paths for auto-execute vs. human review
- **Skill-Based**: Reusable skill definitions in markdown
- **Multi-Watcher**: Flexible trigger system (file, time, email, webhook)

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  File    │  │  Time    │  │  Email   │  │ Webhook  │   │
│  │ Watcher  │  │ Watcher  │  │ Watcher  │  │ Watcher  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        └─────────────┴─────────────┴─────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   ORCHESTRATOR              │
        │   - Event Queue             │
        │   - Deduplication           │
        │   - Prioritization          │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   CONTEXT LOADER            │
        │   - Dashboard.md            │
        │   - Company_Handbook.md     │
        │   - Relevant Skills         │
        │   - Previous Plan.md        │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   REASONING ENGINE          │
        │   - Analyze Situation       │
        │   - Apply Policies          │
        │   - Step-by-Step Logic      │
        │   - Make Decision           │
        │   - Update Plan.md          │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   TASK ROUTER               │
        │   - Check Approval Rules    │
        │   - Evaluate Confidence     │
        │   - Route to Queue          │
        └─────────────┬───────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Needs_Action/    │    │ Needs_Approval/  │
│ (Auto-Execute)   │    │ (Human Review)   │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         │              ┌────────┘
         │              │ [Human Reviews]
         │              │ [Approves/Rejects]
         │              │
         └──────────────┘
                │
                ▼
      ┌──────────────────┐
      │   EXECUTOR        │
      │   - Load Skill    │
      │   - Execute Steps │
      │   - Call MCP      │
      │   - Handle Errors │
      └────────┬──────────┘
               │
               ▼
      ┌──────────────────┐
      │  STATE MANAGER   │
      │  - Update        │
      │    Dashboard.md  │
      │  - Move to Done/ │
      │  - Log Actions   │
      │  - Update Metrics│
      └──────────────────┘
```

## Component Details

### 1. Watchers (Trigger Layer)

**Purpose**: Detect events that require FTE attention

**File Watcher** (`watchers/file_watcher.py`)
- Monitors specified directories for file changes
- Uses watchdog library for efficient monitoring
- Filters by file patterns (*.md by default)
- Deduplicates events within time window

**Time Watcher** (`watchers/time_watcher.py`)
- Checks scheduled tasks periodically
- Supports daily, weekly, interval-based schedules
- Tracks last run time to prevent duplicates
- Configurable via `scheduler/schedule_config.yaml`

**Email Watcher** (stub)
- Polls email inbox for new messages
- Matches against known patterns
- Extracts sender, subject, body

**Webhook Watcher** (stub)
- HTTP server listening for webhooks
- Validates incoming requests
- Transforms to internal event format

### 2. Orchestrator (`core/orchestrator.py`)

**Purpose**: Central coordination and event management

**Responsibilities**:
- Initialize all components
- Manage event queue
- Coordinate processing pipeline
- Handle concurrent tasks
- Update system metrics
- Manage lifecycle (start/stop)

**Key Features**:
- Thread-safe event queue
- Deduplication within configurable window
- Priority-based processing
- Graceful shutdown handling
- Status reporting

### 3. Context Loader (`core/context_loader.py`)

**Purpose**: Load relevant context for reasoning

**Loads**:
- Current Dashboard state
- Company Handbook policies
- Previous reasoning from Plan.md
- Matched skill definition
- Event details

**Skill Matching**:
- Maps event types to skills
- Loads skill definition from SKILLS/
- Provides skill context to reasoning engine

### 4. Reasoning Engine (`core/reasoning_engine.py`)

**Purpose**: Analyze events and make decisions

**Process**:
1. Describe current situation
2. Extract relevant policies from handbook
3. Analyze matched skill requirements
4. Generate step-by-step analysis
5. Make decision (auto-execute or require approval)
6. Calculate confidence level
7. Update Plan.md with full reasoning

**Decision Factors**:
- Skill approval requirements
- Confidence level (< 80% requires approval)
- Risk indicators (delete, external, MCP, API)
- Policy constraints from handbook

### 5. Task Router (`core/task_router.py`)

**Purpose**: Route tasks to appropriate queues

**Routing Logic**:
1. Check reasoning engine recommendation
2. Evaluate confidence threshold
3. Apply approval rules from config
4. Check for high-risk indicators
5. Default to requiring approval (safety-first)

**Creates Task Files**:
- Markdown format with full context
- Includes event details, reasoning, decision
- Placeholder for human approval decision
- Execution log section

### 6. Executor (`core/executor.py`)

**Purpose**: Execute approved tasks

**Process**:
1. Read task file from Needs_Action/
2. Parse task details and matched skill
3. Load skill definition
4. Execute skill steps sequentially
5. Call MCP if required (with approval check)
6. Handle errors with retry logic
7. Return execution results

**Skill Execution**:
- Each skill has defined steps
- Steps executed in order
- Errors logged and handled
- Results captured for reporting

### 7. State Manager (`core/state_manager.py`)

**Purpose**: Manage system state and dashboard

**Responsibilities**:
- Update Dashboard.md with current metrics
- Move completed tasks to Done/ archive
- Track recent activity
- Calculate system health
- Log task completions

**Dashboard Sections**:
- Current state (active, completed, pending)
- Recent activity (last 10 items)
- Metrics (24h window)
- Active watchers status
- Alerts and warnings
- Next scheduled tasks

### 8. MCP Client (`mcp/mcp_client.py`)

**Purpose**: Interface with external MCP servers

**Features**:
- Server registry and configuration
- Enable/disable servers individually
- Timeout and retry handling
- Call logging
- Simulated responses for demo

**Safety**:
- All MCP calls require approval by default
- Configurable per-server settings
- Complete audit trail

## Memory Vault Structure

```
memory/
├── Dashboard.md              # Current system state
├── Company_Handbook.md       # Policies and procedures
├── Plan.md                   # Current reasoning loop
├── Inbox/                    # New items to process
│   └── *.md
├── Needs_Action/             # Auto-approved tasks
│   └── task-*.md
├── Needs_Approval/           # Requires human review
│   └── task-*.md
├── Done/                     # Completed archive
│   └── YYYY-MM/
│       └── task-*.md
└── SKILLS/                   # Skill definitions
    ├── email_responder.skill.md
    ├── report_generator.skill.md
    └── data_analyzer.skill.md
```

## Execution Lifecycle

### Phase 1: Trigger Detection
- Watchers monitor their respective sources
- Events detected and formatted
- Submitted to orchestrator via callback

### Phase 2: Event Aggregation
- Orchestrator receives event
- Checks for duplicates
- Adds to processing queue
- Prioritizes if needed

### Phase 3: Context Loading
- Load Dashboard for current state
- Load Handbook for policies
- Match event to skill
- Load skill definition
- Gather all relevant context

### Phase 4: Reasoning Loop
- Analyze situation
- Apply policies and constraints
- Evaluate skill requirements
- Generate step-by-step reasoning
- Make decision with confidence level
- Update Plan.md with full reasoning

### Phase 5: Task Routing
- Check approval rules
- Evaluate confidence threshold
- Assess risk indicators
- Route to Needs_Action or Needs_Approval
- Create task file with full context

### Phase 6: Human Review (if needed)
- Human reads task file
- Reviews reasoning and decision
- Adds approval decision
- Moves to Needs_Action if approved

### Phase 7: Execution
- Executor picks up task from Needs_Action
- Loads skill definition
- Executes steps sequentially
- Calls MCP if required
- Handles errors with retry
- Captures results

### Phase 8: State Update
- Update Dashboard with results
- Move task to Done/ archive
- Add to recent activity
- Update metrics
- Log completion

## Configuration

### Main Config (`config/fte_config.yaml`)
- System settings
- Memory vault paths
- Watcher configurations
- Orchestrator settings
- MCP settings

### Approval Rules (`config/approval_rules.yaml`)
- Auto-approve conditions
- Require-approval conditions
- Critical-approval conditions
- Confidence thresholds

### Schedule Config (`scheduler/schedule_config.yaml`)
- Scheduled task definitions
- Recurrence patterns
- Task parameters

### MCP Config (`mcp/mcp_config.yaml`)
- MCP server registry
- Server endpoints
- Timeout settings
- Approval requirements

## Safety Features

1. **Default to Approval**: Unknown operations require human review
2. **Confidence Thresholds**: Low confidence escalates to approval
3. **MCP Gating**: External calls require approval by default
4. **Audit Trail**: Complete logging in Plan.md and logs/
5. **Rollback Capability**: All tasks archived in Done/
6. **Error Handling**: Failures escalate to approval queue
7. **Graceful Degradation**: System continues if components fail

## Extensibility

### Adding New Watchers
1. Create `watchers/my_watcher.py`
2. Implement `start()`, `stop()`, `is_running()`
3. Call `event_callback(event)` when triggered
4. Register in orchestrator `_init_watchers()`

### Adding New Skills
1. Create `memory/SKILLS/my_skill.skill.md`
2. Define trigger conditions, steps, approval requirements
3. Add execution logic in `executor._execute_skill()`
4. Update skill matching in `context_loader._match_skill()`

### Adding MCP Servers
1. Edit `mcp/mcp_config.yaml`
2. Add server configuration
3. Implement actual HTTP calls in `mcp_client.py`

## Performance Considerations

- **Event Queue**: Thread-safe, non-blocking
- **Concurrent Tasks**: Configurable max concurrent
- **File Watching**: Efficient watchdog library
- **Deduplication**: Time-window based
- **Logging**: Async where possible

## Future Enhancements

1. **Advanced Reasoning**: LLM integration for complex decisions
2. **Learning**: Track approval patterns, adjust confidence
3. **Multi-Agent**: Coordinate multiple FTEs
4. **Web UI**: Dashboard and approval interface
5. **Metrics**: Prometheus/Grafana integration
6. **Notifications**: Slack/email for approvals
7. **Backup**: Automated memory vault backups
8. **Testing**: Comprehensive test suite

## Conclusion

The Silver Tier Digital FTE provides a robust foundation for autonomous task execution with appropriate human oversight. The local-first, markdown-based approach ensures transparency, auditability, and ease of use while maintaining safety through approval workflows.
