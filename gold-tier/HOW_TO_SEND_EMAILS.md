# How to Send Custom Emails

## New Simple Workflow

### Step 1: Edit the Draft File

Open `draft-email.yaml` and fill in your email content:

```yaml
# Recipient details
to: maryamkhalid261453@gmail.com
subject: Health update

# Email content
recipient_name: Maryam
opening: Hi
body: |
  How are you?

  I hope everything is going well.
closing: Best wishes

# Sender details (optional)
sender_name: Mahnoor Khalid
sender_title: ""
company_name: ""
```

### Step 2: Send the Email

```bash
python send_custom_email.py
```

**Output:**
```
📧 Custom Email Sender
============================================================

Loading draft: draft-email.yaml
To: maryamkhalid261453@gmail.com
Subject: Health update

Sending email to maryamkhalid261453@gmail.com...

✅ Email sent successfully!
   Message ID: 19c5d6fc77595482
   Timestamp: 2026-02-15 00:05:30
```

### Step 3: Check the Email

The recipient will receive a clean, normal email:

```
Dear Maryam,

Hi

How are you?

I hope everything is going well.

Best wishes

Best regards,
Mahnoor Khalid
```

---

## Multiple Email Drafts

You can create multiple draft files:

```bash
# Copy the template
cp draft-email.yaml health-update.yaml
cp draft-email.yaml work-email.yaml

# Edit each file with different content
# Then send specific ones:
python send_custom_email.py health-update.yaml
python send_custom_email.py work-email.yaml
```

---

## What Changed

### Before (Old Way)
- Run command
- Answer questions one by one
- Email sent with template code visible

### After (New Way)
- Edit YAML file with your content
- Run command
- Clean email sent with progress messages

---

## Tips

1. **Keep draft-email.yaml as template** - Copy it for each new email
2. **Use multi-line body** - The `|` symbol lets you write multiple paragraphs
3. **Leave fields empty** - If you don't need sender_title or company_name, leave them as `""`

---

## Example Emails

### Simple Email
```yaml
to: friend@example.com
subject: Quick Hello
recipient_name: Friend
opening: Hey!
body: Just wanted to say hi. Hope you're doing well!
closing: Talk soon
sender_name: Mahnoor
sender_title: ""
company_name: ""
```

### Professional Email
```yaml
to: client@company.com
subject: Project Update
recipient_name: Mr. Johnson
opening: I hope this email finds you well.
body: |
  I wanted to provide you with an update on the project status.

  We have completed Phase 1 and are now moving into Phase 2.
  All deliverables are on track for the agreed timeline.
closing: Please let me know if you have any questions.
sender_name: Mahnoor Khalid
sender_title: Project Manager
company_name: Digital FTE
```

---

## Troubleshooting

### Error: "Draft file not found"
**Solution:** Make sure you're in the silver-tier directory and draft-email.yaml exists

### Error: "to field is required"
**Solution:** Add the recipient email in the YAML file

### Email shows placeholders
**Solution:** Make sure you edited the YAML file, not the template file

---

**That's it! Much simpler than before.** 🎉
