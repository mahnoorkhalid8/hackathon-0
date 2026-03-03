---
id: "{{APPROVAL_ID}}"
created_at: "{{TIMESTAMP_ISO}}"
status: "PENDING"  # PENDING | APPROVED | REJECTED | EXPIRED
action_type: "{{ACTION_TYPE}}"  # email | linkedin_post | api_call | file_delete | financial
priority: "{{PRIORITY}}"  # low | medium | high | critical
expires_at: "{{EXPIRY_TIMESTAMP}}"  # Auto-reject after this time
requested_by: "{{AGENT_NAME}}"
---

# Approval Request: {{ACTION_TITLE}}

## Proposed Action

**Type:** {{ACTION_TYPE}}
**Target:** {{TARGET_DESCRIPTION}}
**Estimated Duration:** {{DURATION}}

### Action Details

{{ACTION_DESCRIPTION}}

### Execution Command

```yaml
mcp_server: "{{MCP_SERVER_NAME}}"
method: "{{METHOD_NAME}}"
parameters:
  {{PARAMETERS_YAML}}
```

## Reasoning

### Context

{{CONTEXT_DESCRIPTION}}

### Why This Action?

{{REASONING_BULLETS}}

### Expected Outcome

{{EXPECTED_OUTCOME}}

## Risk Analysis

### Impact Assessment

- **Impact Level:** {{IMPACT_LEVEL}}  # low | medium | high | critical
- **Reversibility:** {{REVERSIBILITY}}  # reversible | partially_reversible | irreversible
- **Scope:** {{SCOPE}}  # internal | team | public | external
- **Data Sensitivity:** {{DATA_SENSITIVITY}}  # none | low | medium | high | pii

### Potential Risks

1. **{{RISK_1_TITLE}}**
   - Likelihood: {{LIKELIHOOD_1}}
   - Impact: {{IMPACT_1}}
   - Mitigation: {{MITIGATION_1}}

2. **{{RISK_2_TITLE}}**
   - Likelihood: {{LIKELIHOOD_2}}
   - Impact: {{IMPACT_2}}
   - Mitigation: {{MITIGATION_2}}

### Safeguards

- {{SAFEGUARD_1}}
- {{SAFEGUARD_2}}
- {{SAFEGUARD_3}}

## Compliance & Policy

- **Company Policy Check:** {{POLICY_STATUS}}  # compliant | needs_review | violation
- **Regulatory Requirements:** {{REGULATORY_NOTES}}
- **Approval Authority Required:** {{APPROVAL_AUTHORITY}}  # agent | human | manager | legal

## Preview

### Email Preview (if applicable)
```
To: {{EMAIL_TO}}
Subject: {{EMAIL_SUBJECT}}
Body:
{{EMAIL_BODY_PREVIEW}}
```

### LinkedIn Post Preview (if applicable)
```
{{LINKEDIN_POST_PREVIEW}}
```

### API Call Preview (if applicable)
```json
{{API_PAYLOAD_PREVIEW}}
```

## Approval Decision

**Status:** {{STATUS}}
**Decided By:** {{APPROVER_NAME}}
**Decided At:** {{DECISION_TIMESTAMP}}
**Comments:** {{APPROVAL_COMMENTS}}

### If APPROVED:
- Agent will execute the action immediately
- Execution log will be saved to vault/Done/
- Notification will be sent upon completion

### If REJECTED:
- Action will NOT be executed
- Request will be moved to vault/Done/ with REJECTED status
- Agent will log the rejection and continue with next task

### If EXPIRED:
- Action will be auto-rejected after {{EXPIRY_DURATION}}
- Request will be moved to vault/Done/ with EXPIRED status

---

## Human Instructions

To approve this action:
1. Review all sections above carefully
2. Change `status: "PENDING"` to `status: "APPROVED"` in the frontmatter
3. Add your name to `decided_by` field
4. Add any comments in the Approval Decision section
5. Save the file

To reject this action:
1. Change `status: "PENDING"` to `status: "REJECTED"` in the frontmatter
2. Add your name to `decided_by` field
3. Explain reason in the Approval Decision comments section
4. Save the file

**Note:** The agent monitors this file every 30 seconds. Your decision will be processed automatically.
