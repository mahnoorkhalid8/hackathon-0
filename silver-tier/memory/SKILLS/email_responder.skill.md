# Skill: Email Responder

**ID:** email_responder
**Version:** 1.0
**Approval Required:** Conditional

---

## Description

Automatically respond to routine emails based on predefined templates and context.

---

## Trigger Conditions

- New email detected in inbox
- Email matches known patterns (greetings, status requests, confirmations)
- Sender is in known contacts list

---

## Required Inputs

- `sender_email`: Email address of sender
- `subject`: Email subject line
- `body`: Email body content
- `sentiment`: Detected sentiment (positive/neutral/negative)

---

## Execution Steps

1. Analyze email content and intent
2. Check Company_Handbook.md for response policies
3. Select appropriate response template
4. Generate personalized response
5. If auto-approve conditions met: send response
6. Otherwise: move to Needs_Approval/ with draft

---

## Auto-Approve Conditions

- Sender in known_contacts list
- Sentiment is positive or neutral
- No attachments present
- Request is informational only
- No financial or commitment implications

---

## Expected Outputs

- `response_draft`: Generated email response
- `confidence`: Confidence level (0-100)
- `action`: "send" or "approve_required"

---

## Error Handling

- If sender unknown: require approval
- If sentiment negative: require approval
- If intent unclear: require approval
- If template not found: require approval

---

## Examples

**Auto-Approve:**
- "Thanks for the update!"
- "What's the status of project X?"
- "Can you send me the report?"

**Require Approval:**
- "We need to discuss pricing"
- "Please delete this data"
- "Can you commit to this deadline?"
