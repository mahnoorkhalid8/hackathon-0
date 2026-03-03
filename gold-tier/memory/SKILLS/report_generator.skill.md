# Skill: Report Generator

**ID:** report_generator
**Version:** 1.0
**Approval Required:** Yes

---

## Description

Generate reports from data sources using predefined templates and formatting.

---

## Trigger Conditions

- Scheduled time reached (e.g., weekly report)
- Manual request via Inbox/
- External webhook trigger

---

## Required Inputs

- `report_type`: Type of report (weekly, monthly, custom)
- `data_source`: Path to data or MCP endpoint
- `template`: Report template name
- `output_format`: markdown, pdf, html

---

## Execution Steps

1. Load report template from SKILLS/templates/
2. Fetch data from specified source
3. If external MCP required: request approval
4. Process and aggregate data
5. Generate report using template
6. Save to Done/ with timestamp
7. Update Dashboard.md with completion

---

## Auto-Approve Conditions

- Data source is local file
- Template is pre-approved
- No external API calls required

---

## Expected Outputs

- `report_file`: Path to generated report
- `summary`: Brief summary of findings
- `data_points`: Number of data points processed

---

## Error Handling

- If data source unavailable: log error, notify human
- If template missing: use default template, flag for review
- If MCP call fails: retry once, then require approval

---

## MCP Integration

This skill may require MCP calls for:
- External data fetching
- API integrations
- Web scraping

All MCP calls require human approval per Company_Handbook.md policy.
