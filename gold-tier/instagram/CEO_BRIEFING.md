# CEO Briefing System

Automated executive reporting for Instagram Business with analytics, system health monitoring, and marketing ROI.

## Features

- **Performance Analytics**: Impressions, reach, engagement, saves
- **Marketing ROI**: Cost per post, cost per engagement, cost per 1K impressions
- **Top Performing Post**: Highlights best content
- **System Health**: Token expiration warnings, critical error alerts
- **Automated Scheduling**: Weekly Monday morning reports
- **MCP Integration**: Available as agent tool

## Quick Start

### Generate Briefing Now

```bash
python ceo_briefing.py
```

Or specify days:
```bash
python ceo_briefing.py 14  # Last 14 days
```

### Schedule Automated Reports

```bash
python schedule_briefing.py
```

Runs every Monday at 8:00 AM.

### Use as MCP Tool

The CEO briefing is available as an MCP tool:

```python
# Via MCP server
tool: generate_ceo_briefing
arguments:
  days: 7
  save: true
```

## Report Sections

### 1. System Status
- ✅ Healthy
- ⚠️ Warnings (token expiring soon)
- 🚨 Critical Issues (token expired, system errors)

### 2. Performance Metrics
- Total Posts
- Total Impressions
- Total Reach
- Total Engagement
- Engagement Rate
- Total Saved

### 3. Marketing Investment
- Cost per Post: $5.00
- Total Marketing Cost
- Cost per Engagement
- Cost per 1K Impressions

### 4. Top Performing Post
- Caption preview
- Posted date
- Link to post
- Performance metrics
- Engagement rate

### 5. Recent Posts Summary
- Last 10 posts
- Date, caption, engagement, impressions, reach

### 6. Recommendations
- Posting frequency suggestions
- Engagement rate optimization
- Cost efficiency improvements
- Content strategy insights

## Example Report

```markdown
# Instagram Business - CEO Briefing
**Report Date:** March 05, 2026
**Period:** Feb 27 - Mar 05, 2026 (7 days)

---

## 📊 Executive Summary

### ✅ System Status: Healthy

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Total Posts** | 5 |
| **Total Impressions** | 12,450 |
| **Total Reach** | 8,320 |
| **Total Engagement** | 456 |
| **Engagement Rate** | 3.66% |
| **Total Saved** | 23 |

## 💰 Marketing Investment

| Metric | Value |
|--------|-------|
| **Cost per Post** | $5.00 |
| **Total Marketing Cost** | $25.00 |
| **Cost per Engagement** | $0.0548 |
| **Cost per 1K Impressions** | $2.01 |

## 🏆 Top Performing Post

**Caption:** Beautiful sunset at the beach 🌅...

**Posted:** 2026-03-03T18:30:00+00:00

**Link:** https://www.instagram.com/p/ABC123/

**Performance:**
- Engagement: 156
- Impressions: 3,240
- Reach: 2,180
- Saved: 12
- Engagement Rate: 4.81%

## 💡 Recommendations

- **Replicate success** - Analyze what made the top post successful
- Engagement rate is above industry average (3.66% vs 2-3%)
- Cost per engagement is efficient ($0.0548)
```

## Configuration

### Marketing Costs

Edit `ceo_briefing.py`:

```python
class CEOBriefingGenerator:
    COST_PER_POST = 5.00  # Change to your actual cost
```

### Schedule Time

Edit `schedule_briefing.py`:

```python
# Change from Monday 8:00 AM to your preferred time
schedule.every().monday.at("08:00").do(generate_and_send_briefing)

# Or daily:
schedule.every().day.at("09:00").do(generate_and_send_briefing)
```

### Report Period

```bash
# Last 7 days (default)
python ceo_briefing.py

# Last 30 days
python ceo_briefing.py 30

# Custom period
python schedule_briefing.py --now --days 14
```

## System Health Monitoring

The briefing automatically checks:

### Token Expiration
- **Warning**: Token expires within 7 days
- **Critical**: Token already expired
- **Action**: Provides refresh command

### Critical Errors
- Checks `../logs/ceo_briefing.json` for recent critical errors
- Shows top 3 issues
- Provides remediation steps

### Example Alerts

**Warning:**
```
⚠️ System Warnings

- token_expiring_soon: Access token expires on 2026-03-15
  - Recommended Action: `python cli.py refresh`
```

**Critical:**
```
🚨 CRITICAL SYSTEM ISSUES

- instagram_token_expired: Instagram access token expired. Manual refresh required.
  - Action Required: `Run: python cli.py refresh`
```

## Integration with Autonomous Employee

The CEO briefing integrates with your autonomous employee system:

1. **Scheduled Generation**: Runs every Monday morning
2. **Critical Alerts**: Logs to CEO briefing file
3. **MCP Tool**: Available for agent queries
4. **Email Integration**: Ready for email delivery (TODO)

## Output Files

Reports are saved to:
```
reports/
├── ceo_briefing_20260305_080000.md
├── ceo_briefing_20260312_080000.md
└── ceo_briefing_20260319_080000.md
```

## CLI Commands

```bash
# Generate now
python ceo_briefing.py

# Generate for specific period
python ceo_briefing.py 14

# Schedule automated reports
python schedule_briefing.py

# Generate once and exit
python schedule_briefing.py --now

# Custom period
python schedule_briefing.py --now --days 30
```

## MCP Server Integration

The CEO briefing is available as an MCP tool in `social_media_server.py`:

```python
# Tool definition
{
  "name": "generate_ceo_briefing",
  "description": "Generate executive briefing with Instagram analytics, system health, and marketing ROI",
  "inputSchema": {
    "days": 7,      # Number of days to analyze
    "save": true    # Save report to file
  }
}
```

## Metrics Explained

### Engagement
Total interactions (likes + comments + saves + shares)

### Impressions
Total number of times content was displayed

### Reach
Unique accounts that saw the content

### Engagement Rate
(Engagement / Impressions) × 100

### Cost per Engagement
Total Marketing Cost / Total Engagement

### Cost per 1K Impressions
(Total Marketing Cost / Total Impressions) × 1000

## Troubleshooting

### "No posts in the last 7 days"
- Check that posts were actually published
- Verify Instagram Business account connection
- Check token permissions

### "Failed to fetch media"
- Verify access token is valid
- Check Instagram Business ID
- Ensure proper API permissions

### "Token expired"
- Run: `python cli.py refresh`
- Update IG_TOKEN_EXPIRES_AT in .env

## Next Steps

1. Review weekly briefings every Monday
2. Act on system health warnings
3. Analyze top performing content
4. Adjust posting strategy based on recommendations
5. Monitor cost per engagement trends

## Email Integration (Coming Soon)

To enable email delivery:

1. Configure SMTP settings
2. Update `send_briefing_email()` in `schedule_briefing.py`
3. Set CEO_EMAIL in .env
4. Restart scheduler

## Support

- Full system docs: `FINAL_DELIVERY.md`
- Workflow guide: `WORKFLOW.md`
- Error recovery: `ERROR_RECOVERY.md`
