# Skill: Data Analyzer

**ID:** data_analyzer
**Version:** 1.0
**Approval Required:** Conditional

---

## Description

Analyze data from local or external sources and generate insights.

---

## Trigger Conditions

- Data analysis request in Inbox/
- Scheduled data processing task
- API webhook with data payload

---

## Required Inputs

- `data_source`: Path to data file or API endpoint
- `analysis_type`: Type of analysis (summary, trend, comparison)
- `output_format`: Format for results (markdown, json, csv)

---

## Execution Steps

1. Validate data source accessibility
2. Load data into memory
3. Perform requested analysis
4. Generate visualizations if applicable
5. Create summary report
6. Save results to Done/

---

## Auto-Approve Conditions

- Data source is local file
- Read-only operation
- No external API calls
- File size < 10MB

---

## Expected Outputs

- `analysis_report`: Path to generated report
- `insights`: Key findings (list)
- `data_points_analyzed`: Count of records processed

---

## Error Handling

- If data source unavailable: log error, require approval for retry
- If data format invalid: attempt auto-detection, fallback to approval
- If analysis fails: save partial results, notify human

---

## Examples

**Auto-Approve:**
- Analyze local CSV file
- Generate summary statistics
- Create trend chart from logs

**Require Approval:**
- Fetch data from external API
- Process sensitive information
- Large dataset (>10MB)
