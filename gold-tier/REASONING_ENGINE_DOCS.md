# Iterative Reasoning Engine - Documentation

## Overview

The Iterative Reasoning Engine is a sophisticated task execution system that breaks down complex objectives into manageable steps, executes them one at a time, and continuously updates an execution plan (Plan.md) with progress and reasoning.

## Key Features

### 1. **Automatic Task Decomposition**
- Analyzes objectives and breaks them into executable steps
- Identifies dependencies between steps
- Classifies task types (data processing, report generation, integration, etc.)
- Auto-generates appropriate step sequences

### 2. **Iterative Execution**
- Executes one step at a time
- Updates Plan.md after each step
- Re-evaluates plan state continuously
- Adapts to changing conditions

### 3. **Failure Recovery**
- Automatic retry with configurable attempts (default: 3)
- Multiple recovery strategies:
  - **RETRY**: Try again immediately
  - **ALTERNATIVE**: Use alternative approach
  - **SKIP_AND_CONTINUE**: Skip non-critical step
  - **ABORT**: Stop and request human intervention

### 4. **Transparent Reasoning**
- All decisions documented in Plan.md
- Step-by-step execution log
- Clear status tracking
- Human-readable progress updates

### 5. **Human-in-the-Loop**
- Requests intervention when needed
- Low confidence situations escalate
- Critical failures require approval
- Clear approval workflow

## Architecture

```
Task Input
    ↓
Analyze & Create Plan
    ↓
┌─────────────────────────┐
│  Iterative Execution    │
│  Loop:                  │
│  1. Get next step       │
│  2. Execute step        │
│  3. Update Plan.md      │
│  4. Re-evaluate         │
│  5. Check if complete   │
│  6. Repeat              │
└─────────────────────────┘
    ↓
Finalize & Generate Summary
    ↓
Completed Plan
```

## Usage

### Basic Usage

```python
from iterative_reasoning_engine import IterativeReasoningEngine

# Initialize engine
config = {'plans_dir': 'memory/plans'}
engine = IterativeReasoningEngine(config)

# Define task
task = {
    'objective': 'Generate weekly sales report',
    'priority': 'HIGH',
    'success_criteria': [
        'Data collected from all sources',
        'Analysis completed',
        'Report generated'
    ]
}

# Create and execute plan
plan = engine.analyze_and_create_plan(task)
result = engine.execute_plan_iteratively(plan)

# Check results
print(f"Status: {result.status.value}")
print(f"Plan file: memory/plans/{plan.id}.md")
```

### With Explicit Steps

```python
task = {
    'objective': 'Process customer data',
    'steps': [
        {
            'name': 'Load Data',
            'description': 'Load customer data from database',
            'actions': ['connect_db', 'query_data', 'export_csv'],
            'expected_outputs': ['customers.csv']
        },
        {
            'name': 'Clean Data',
            'description': 'Remove duplicates and validate',
            'actions': ['remove_duplicates', 'validate_fields'],
            'expected_outputs': ['customers_clean.csv'],
            'dependencies': ['step-001']
        },
        {
            'name': 'Generate Report',
            'description': 'Create summary report',
            'actions': ['calculate_stats', 'create_charts'],
            'expected_outputs': ['report.pdf'],
            'dependencies': ['step-002']
        }
    ]
}

plan = engine.analyze_and_create_plan(task)
result = engine.execute_plan_iteratively(plan)
```

### Auto-Generated Steps

```python
# Engine will automatically decompose based on task type
task = {
    'objective': 'Analyze sales data and generate insights',
    'priority': 'MEDIUM'
}

# Engine detects this is a data processing task
# and generates appropriate steps automatically
plan = engine.analyze_and_create_plan(task)
```

## Plan.md Structure

The engine generates and maintains a Plan.md file with this structure:

```markdown
# Execution Plan: [Objective]

**Plan ID:** plan-20260213-143022
**Status:** IN_PROGRESS

## Objective
[Clear statement of what needs to be accomplished]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Execution Steps

### Step 1: [Name]
**ID:** step-001
**Status:** COMPLETED
**Attempts:** 1/3

**Description:** [What this step does]

**Actions:**
- action_1
- action_2

**Notes:** [Observations and issues]

---

### Step 2: [Name]
**ID:** step-002
**Status:** IN_PROGRESS
...

## Current State
**Progress:** 1/3 steps completed
**Completion:** 33%

## Completion Summary
[Generated when plan completes]
```

## Step Status Flow

```
PENDING → IN_PROGRESS → COMPLETED
                      → FAILED → PENDING (retry)
                              → FAILED (max attempts)
                      → SKIPPED
                      → BLOCKED
```

## Plan Status Flow

```
NOT_STARTED → IN_PROGRESS → COMPLETED
                          → FAILED
                          → BLOCKED
                          → AWAITING_APPROVAL
                          → OBSOLETE
```

## Failure Recovery

### Automatic Retry
- Steps retry up to 3 times by default
- Configurable per step: `max_attempts`
- Retry strategies:
  - Immediate retry
  - Retry with modifications
  - Skip and continue

### Recovery Strategies

**Critical Step Fails:**
```
1. Attempt retry (up to max_attempts)
2. If still failing, check for alternative approach
3. If no alternative, request human intervention
4. Plan status → AWAITING_APPROVAL
```

**Non-Critical Step Fails:**
```
1. Attempt retry
2. If still failing, skip and continue
3. Mark step as SKIPPED
4. Continue with remaining steps
5. Note degraded functionality in summary
```

### Human Intervention Triggers

- Critical step fails after max attempts
- Confidence level < 70%
- Unexpected results encountered
- High-risk next step detected
- Multiple steps have failed (≥2)

## Extending the Engine

### Custom Action Execution

Override `_execute_action` to implement actual work:

```python
class MyReasoningEngine(IterativeReasoningEngine):
    def _execute_action(self, action: str, step: Step, plan: Plan):
        if action == 'fetch_data':
            return self.fetch_data_from_db()
        elif action == 'process_data':
            return self.process_data()
        else:
            return super()._execute_action(action, step, plan)

    def fetch_data_from_db(self):
        # Your implementation
        pass
```

### Custom Step Validation

Override `_validate_step_outputs`:

```python
def _validate_step_outputs(self, step: Step, outputs: Dict) -> bool:
    # Custom validation logic
    if step.id == 'step-001':
        return 'data_file' in outputs and outputs['data_file']['size'] > 0
    return super()._validate_step_outputs(step, outputs)
```

### Custom Task Decomposition

Override `_decompose_into_steps`:

```python
def _decompose_into_steps(self, objective: str, context: Dict, task: Dict):
    if 'custom_task_type' in task:
        return self._create_custom_steps(task)
    return super()._decompose_into_steps(objective, context, task)
```

## Best Practices

### 1. Define Clear Success Criteria
```python
task = {
    'objective': 'Generate report',
    'success_criteria': [
        'All data sources accessed successfully',
        'Report contains all required sections',
        'Quality checks passed',
        'Output file size < 10MB'
    ]
}
```

### 2. Mark Critical Steps
```python
{
    'name': 'Fetch Customer Data',
    'is_critical': True,  # Failure will stop execution
    'actions': [...]
}
```

### 3. Set Appropriate Dependencies
```python
{
    'name': 'Generate Charts',
    'dependencies': ['step-001', 'step-002'],  # Requires both steps
    'actions': [...]
}
```

### 4. Use Descriptive Action Names
```python
# Good
'actions': ['connect_to_database', 'execute_query', 'export_to_csv']

# Bad
'actions': ['do_stuff', 'process', 'finish']
```

### 5. Monitor Plan Files
```bash
# Watch plan updates in real-time
tail -f memory/plans/plan-20260213-143022.md
```

## Examples

See `demo_reasoning_engine.py` for complete examples:

1. **Simple Task** - Basic 3-step execution
2. **Complex Task** - Multi-step with failure recovery
3. **Auto-Generated** - Engine creates steps automatically

Run demos:
```bash
python demo_reasoning_engine.py
```

## Integration with Digital FTE

The Iterative Reasoning Engine integrates with the Silver Tier Digital FTE:

```python
# In orchestrator.py
from iterative_reasoning_engine import IterativeReasoningEngine

class Orchestrator:
    def __init__(self, config):
        self.reasoning_engine = IterativeReasoningEngine(config)

    def handle_task(self, task):
        # Create plan
        plan = self.reasoning_engine.analyze_and_create_plan(task)

        # Execute iteratively
        result = self.reasoning_engine.execute_plan_iteratively(plan)

        # Handle result
        if result.status == PlanStatus.COMPLETED:
            self.move_to_done(result)
        elif result.status == PlanStatus.AWAITING_APPROVAL:
            self.move_to_approval_queue(result)
```

## Troubleshooting

### Plan Not Progressing
- Check step dependencies are met
- Verify no circular dependencies
- Check for blocked steps

### Steps Failing Repeatedly
- Review step actions
- Check resource availability
- Verify expected outputs are achievable

### Plan File Not Updating
- Check write permissions on plans_dir
- Verify path exists
- Check for file system errors

## Performance Considerations

- **Step Granularity**: Balance between too fine-grained (overhead) and too coarse (lack of progress visibility)
- **Retry Limits**: Set appropriate max_attempts based on action reliability
- **Plan File Updates**: Written after each step (can be optimized for high-frequency updates)
- **Memory Usage**: Plans kept in memory during execution

## Future Enhancements

- [ ] Parallel step execution (for independent steps)
- [ ] Plan versioning and rollback
- [ ] Learning from past executions
- [ ] Predictive failure detection
- [ ] Resource usage tracking
- [ ] Cost estimation
- [ ] Performance profiling
- [ ] Plan templates library

---

**Version:** 1.0.0
**Last Updated:** 2026-02-13
**Status:** Production Ready
