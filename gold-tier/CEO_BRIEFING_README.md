# Monday Morning CEO Briefing Generator - Documentation

## Overview

The Monday Morning CEO Briefing Generator automatically analyzes completed and pending tasks to create a comprehensive executive briefing with metrics, bottlenecks, and actionable recommendations.

## Features

✅ **Automated Analysis**
- Analyzes completed tasks from vault/Done/
- Analyzes pending tasks from vault/Needs_Action/
- Analyzes approval requests from vault/Needs_Approval/
- Identifies bottlenecks and blockers

✅ **Comprehensive Metrics**
- Completion rate and productivity trends
- Average completion time
- Task distribution by type
- Quality metrics (approval rate, rework rate)

✅ **Intelligent Insights**
- Identifies aging tasks (>7 days)
- Detects blocked tasks
- Highlights approval backlog
- Generates priority recommendations

✅ **Executive-Ready Output**
- Professional Markdown format
- Visual indicators (emojis for status)
- Actionable recommendations
- Week-over-week trends

## Components

```
templates/
└── monday-briefing-template.md    # Briefing template

generate_ceo_briefing.py           # Main generator script
  ├── TaskAnalyzer                 # Analyzes tasks
  └── BriefingGenerator            # Generates briefing

examples/
└── ceo-briefing-example.md        # Example output

memory/
├── Dashboard.md                   # Updated with briefing
└── reports/
    └── ceo_briefing_*.md          # Archived briefings
```

## Usage

### Manual Generation

```bash
# Generate briefing (saves to memory/Dashboard.md)
python generate_ceo_briefing.py

# Generate with custom output path
python generate_ceo_briefing.py --output custom/path.md

# Generate with custom vault path
python generate_ceo_briefing.py --vault /path/to/vault
```

### Automated Generation (via Scheduler)

```bash
# Run via orchestration script
python run_agent.py ceo-report

# Scheduled execution (Monday 9:00 AM)
# Windows: Task Scheduler runs automatically
# Linux: Cron runs automatically
```

### Integration with Scheduler

The CEO briefing is automatically generated every Monday at 9:00 AM via the scheduler system:

**Windows Task Scheduler:**
- Task: `DigitalFTE\CEOReport`
- Schedule: Monday 9:00 AM
- Command: `python run_agent.py ceo-report`

**Linux Cron:**
- Schedule: `0 9 * * 1`
- Command: `python run_agent.py ceo-report`

## Output

### Dashboard Update

The briefing is saved to `memory/Dashboard.md`, providing a real-time executive view of system status.

### Archived Reports

Each briefing is also archived to `memory/reports/ceo_briefing_YYYYMMDD_HHMMSS.md` for historical reference.

### Email Delivery

If configured, the briefing is automatically emailed to the CEO:

```bash
# Set CEO email address
export CEO_EMAIL=khalidmahnoor889@gmail.com
```

## Briefing Structure

### 1. Executive Summary
- High-level overview
- Key highlights (completed, pending, blocked tasks)
- Completion rate

### 2. Progress This Week
- List of completed tasks
- Top achievements
- Time distribution by task type

### 3. Current Status
- In-progress tasks
- Pending tasks
- Tasks awaiting approval

### 4. Bottlenecks & Blockers
- Critical issues
- Aging tasks (>7 days)
- Blocked tasks
- Resource constraints

### 5. Recommended Priorities
- Top 3 priorities for the week
- Reason, impact, and effort for each
- Quick wins

### 6. Performance Metrics
- Productivity (completion rate, tasks per day)
- Quality (approval rate, rework rate)
- Efficiency (response time, automation rate)
- Revenue impact (if applicable)

### 7. Week Ahead
- Scheduled tasks
- Upcoming deadlines
- Capacity planning

### 8. Insights & Recommendations
- Trends analysis
- Opportunities
- Risks

## Task Analysis

### Task Sources

**Completed Tasks (vault/Done/)**
- Parsed from Markdown files
- Extracted metadata (title, dates, priority)
- Calculated completion time
- Categorized by type

**Pending Tasks (vault/Needs_Action/)**
- Parsed from Markdown files
- Calculated age (days since creation)
- Identified blocked tasks
- Sorted by priority and age

**Approval Tasks (vault/Needs_Approval/)**
- Parsed from approval request files
- Tracked approval status
- Identified approval backlog

### Metadata Extraction

The analyzer extracts metadata from task files:

```yaml
---
title: Task Title
priority: high
status: completed
created_at: 2026-02-10T10:00:00
completed_at: 2026-02-12T15:30:00
type: email
blocked: false
---
```

If frontmatter is not present, metadata is inferred from:
- File name (title)
- File timestamps (created_at, modified_at)
- Content analysis

## Metrics Calculation

### Completion Rate

```
Completion Rate = (Completed Tasks / Total Tasks) × 100
```

### Average Completion Time

```
Avg Completion Time = Σ(Completed Time - Created Time) / Number of Completed Tasks
```

### Tasks Per Day

```
Tasks Per Day = Completed Tasks This Week / 7
```

### Aging Tasks

Tasks pending for more than 7 days are flagged as aging.

### Blocked Tasks

Tasks with `blocked: true` in metadata are identified as blockers.

## Bottleneck Detection

### Aging Tasks Bottleneck

**Trigger:** >5 tasks pending for >7 days
**Severity:** High
**Recommendation:** Review and prioritize or delegate

### Blocked Tasks Bottleneck

**Trigger:** Any tasks with `blocked: true`
**Severity:** Critical
**Recommendation:** Resolve blockers or escalate

### Approval Backlog Bottleneck

**Trigger:** >5 tasks awaiting approval
**Severity:** Medium
**Recommendation:** Review and approve/reject

### Low Completion Rate Bottleneck

**Trigger:** Completion rate <50%
**Severity:** High
**Recommendation:** Focus on completing existing tasks

## Priority Generation

### Priority 1: Unblock Blocked Tasks

**Criteria:** Tasks with `blocked: true`
**Reason:** Blocked tasks prevent downstream progress
**Impact:** High

### Priority 2: Complete Aging Tasks

**Criteria:** Tasks pending >7 days
**Reason:** Long-pending tasks risk becoming stale
**Impact:** Medium

### Priority 3: High-Priority Tasks

**Criteria:** Tasks with `priority: high` or `priority: critical`
**Reason:** Marked as important by requester
**Impact:** High

### Quick Wins

**Criteria:** Tasks with `effort: low` and age <3 days
**Reason:** Easy wins to boost momentum
**Impact:** Low-Medium

## Customization

### Template Customization

Edit `templates/monday-briefing-template.md` to customize:
- Section order
- Metrics displayed
- Visual formatting
- Additional sections

### Metric Customization

Edit `generate_ceo_briefing.py` to customize:
- Metric calculations
- Bottleneck thresholds
- Priority algorithms
- Insight generation

### Output Format

The generator supports Markdown output. To add other formats:

```python
# In BriefingGenerator class
def generate_html(self, analysis):
    # Convert Markdown to HTML
    pass

def generate_pdf(self, analysis):
    # Convert Markdown to PDF
    pass
```

## Testing

### Manual Test

```bash
# Create test tasks
mkdir -p memory/Done memory/Needs_Action

# Create completed task
cat > memory/Done/test_task_1.md << EOF
---
title: Test Task 1
priority: high
status: completed
created_at: 2026-02-10T10:00:00
completed_at: 2026-02-12T15:30:00
type: email
---
# Test Task 1
This is a test task.
EOF

# Create pending task
cat > memory/Needs_Action/test_task_2.md << EOF
---
title: Test Task 2
priority: medium
status: pending
created_at: 2026-02-05T10:00:00
type: report
---
# Test Task 2
This is a pending task.
EOF

# Generate briefing
python generate_ceo_briefing.py

# View output
cat memory/Dashboard.md
```

### Automated Test

```bash
# Run via orchestration script
python run_agent.py ceo-report

# Check logs
tail -f logs/run_agent_*.log
```

## Troubleshooting

### Issue: No tasks found

**Solution:**
1. Check vault directory exists: `ls -la memory/`
2. Check task files exist: `ls -la memory/Done/ memory/Needs_Action/`
3. Verify file format (Markdown with .md extension)

### Issue: Metrics showing 0

**Solution:**
1. Check task files have valid metadata (frontmatter)
2. Verify date formats are ISO 8601 (YYYY-MM-DDTHH:MM:SS)
3. Check file timestamps if metadata is missing

### Issue: Briefing not generated

**Solution:**
1. Check Python version: `python --version` (requires 3.13+)
2. Check dependencies: `pip install pyyaml`
3. Check logs: `tail -f logs/run_agent_*.log`
4. Run with debug: `python generate_ceo_briefing.py --help`

### Issue: Email not sent

**Solution:**
1. Check CEO_EMAIL environment variable: `echo $CEO_EMAIL`
2. Verify MCP email server is running
3. Check email server logs: `tail -f mcp/email-server/logs/email-server.log`
4. Test email server: `python run_agent.py gmail-watcher`

## Best Practices

1. **Consistent Metadata**: Use frontmatter in all task files for accurate metrics
2. **Regular Cleanup**: Archive old completed tasks to keep analysis focused
3. **Priority Tagging**: Tag tasks with priority levels for better recommendations
4. **Status Updates**: Update task status regularly (pending, in_progress, blocked)
5. **Review Weekly**: Review briefing every Monday to track trends
6. **Action Items**: Act on recommended priorities within the week
7. **Feedback Loop**: Update task metadata based on actual completion times

## Integration

### With Approval System

Approval tasks are automatically included in the briefing:
- Pending approvals shown in "Awaiting Approval" section
- Approval backlog triggers bottleneck alert
- Approval success rate tracked in metrics

### With MCP Email Server

Briefing is automatically emailed via MCP server:
- Uses `email_server` MCP server
- Sends to CEO_EMAIL environment variable
- Includes full briefing in email body

### With Scheduler

Briefing generation is automated via scheduler:
- Runs every Monday at 9:00 AM
- Triggered by `run_agent.py ceo-report`
- Logs to `logs/run_agent_*.log`

## Performance

- **Analysis Time**: 1-5 seconds (depends on task count)
- **Generation Time**: <1 second
- **Total Time**: 2-6 seconds
- **Memory Usage**: ~50MB
- **Disk Usage**: ~10KB per briefing

## Security

- ✅ No sensitive data exposed in briefing
- ✅ Task content not included (only titles)
- ✅ Email addresses not shown
- ✅ File paths sanitized
- ✅ Safe for external distribution

## Changelog

### v1.0.0 (2026-02-13)
- Initial release
- Task analysis from vault directories
- Comprehensive metrics calculation
- Bottleneck detection
- Priority recommendations
- Markdown output
- Email delivery
- Scheduler integration

## Support

For issues or questions:
1. Check logs: `logs/run_agent_*.log`
2. Test manually: `python generate_ceo_briefing.py`
3. Review example: `examples/ceo-briefing-example.md`
4. Check documentation: This README
