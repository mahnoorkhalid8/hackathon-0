# LinkedIn Automation - Quick Reference

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| **Strategy Generator** | Create comprehensive content strategy | `python linkedin_strategy_generator.py --interactive` |
| **Post Generator** | Generate posts for all pillars | `python linkedin_post_generator.py --pillar all` |
| **Calendar Generator** | Create weekly/monthly calendar | `python linkedin_calendar_generator.py --weeks 4` |
| **Lead Tracker** | Track and manage leads | `python linkedin_lead_tracker.py --action add` |

---

## Quick Commands

### Generate Complete Strategy
```bash
python linkedin_strategy_generator.py \
  --business "AI automation consulting" \
  --target "small businesses" \
  --goal "generate 10 leads per month"
```

### Generate Posts by Pillar
```bash
# Educational posts
python linkedin_post_generator.py --pillar educational --count 3

# Social proof posts
python linkedin_post_generator.py --pillar social_proof --count 2

# Engagement posts
python linkedin_post_generator.py --pillar engagement --count 2

# Promotional posts
python linkedin_post_generator.py --pillar promotional --count 1

# All pillars
python linkedin_post_generator.py --pillar all --count 3
```

### Generate Content Calendar
```bash
# 4-week calendar starting next Monday
python linkedin_calendar_generator.py --weeks 4

# Custom start date
python linkedin_calendar_generator.py --weeks 8 --start-date 2026-03-01

# Without promotional posts
python linkedin_calendar_generator.py --weeks 4 --no-promotional
```

### Lead Tracking
```bash
# Add new lead
python linkedin_lead_tracker.py --action add

# List all leads
python linkedin_lead_tracker.py --action list

# View lead details
python linkedin_lead_tracker.py --action view --id 1

# Update lead stage
python linkedin_lead_tracker.py --action update --id 1 --stage qualified

# Add interaction
python linkedin_lead_tracker.py --action interact --id 1

# View statistics
python linkedin_lead_tracker.py --action stats
```

---

## Content Pillars

| Pillar | Percentage | Purpose | Example |
|--------|-----------|---------|---------|
| Educational | 40% | Thought leadership | How-to guides, frameworks |
| Social Proof | 30% | Build credibility | Case studies, testimonials |
| Engagement | 20% | Foster community | Questions, discussions |
| Promotional | 10% | Drive conversions | Offers, resources |

---

## Weekly Schedule

| Day | Time | Pillar | Format | CTA |
|-----|------|--------|--------|-----|
| Monday | 9:00 AM | Educational | Carousel/Article | Save this |
| Tuesday | 12:00 PM | Engagement | Question/Poll | Comment below |
| Wednesday | 10:00 AM | Social Proof | Case Study | DM me |
| Thursday | 2:00 PM | Educational | Video/Infographic | Follow for more |
| Friday | 11:00 AM | Engagement | Behind-the-scenes | What's your take? |

---

## Lead Stages

1. **new** - Just discovered
2. **contacted** - Initial outreach made
3. **qualified** - Meets criteria
4. **consultation** - Call scheduled/completed
5. **proposal** - Proposal sent
6. **won** - Converted to customer
7. **lost** - Not interested/no response

---

## Success Metrics

### Month 1: Foundation
- 20 posts published
- 100 new connections
- 200 profile views
- 2-3 leads

### Month 2: Growth
- 20 posts published
- 150 new connections
- 400 profile views
- 5-7 leads

### Month 3: Momentum
- 20 posts published
- 200 new connections
- 600 profile views
- 10+ leads

### Month 4+: Scale
- Consistent lead flow
- Established thought leadership
- Growing community
- Predictable revenue

---

## Complete Workflow Example

```bash
# Step 1: Generate strategy
python linkedin_strategy_generator.py \
  --business "AI automation consulting" \
  --target "small businesses" \
  --goal "generate 10 leads per month"

# Step 2: Review Plan.md and customize

# Step 3: Generate 4-week calendar
python linkedin_calendar_generator.py --weeks 4

# Step 4: Review content_calendar.md

# Step 5: Generate posts for Week 1
python linkedin_post_generator.py --pillar educational --count 2
python linkedin_post_generator.py --pillar engagement --count 2
python linkedin_post_generator.py --pillar social_proof --count 1

# Step 6: Review generated_posts.json and customize

# Step 7: Start posting and tracking leads
python linkedin_lead_tracker.py --action add

# Step 8: Weekly review
python linkedin_lead_tracker.py --action stats
```

---

## Output Files

| File | Description |
|------|-------------|
| `Plan.md` | Comprehensive content strategy |
| `content_calendar.json` | Structured calendar data |
| `content_calendar.md` | Human-readable calendar |
| `generated_posts.json` | Generated posts library |
| `leads.json` | Lead tracking database |

---

## Tips for Success

### Content Creation
- Hook in first line (grab attention)
- Provide actionable value
- Use line breaks for readability
- 1,300-2,000 characters optimal
- Include visuals when possible

### Engagement
- Respond to comments within 1 hour
- Engage with 10 target posts daily
- Be genuine, add value
- Tag strategically

### Lead Generation
- 80% soft CTAs ("Save this")
- 15% medium CTAs ("DM for info")
- 5% hard CTAs ("Book now")
- Follow up within 24 hours

---

## Troubleshooting

**"UnicodeEncodeError"**
- Windows console encoding issue
- Run: `chcp 65001` before scripts
- Or use Git Bash / WSL

**"No posts generated"**
- Check command syntax
- Verify you're in linkedin/ directory
- Try with --pillar all flag

**"Calendar not created"**
- Check date format (YYYY-MM-DD)
- Verify weeks parameter is positive
- Check write permissions

---

For complete documentation, see `README.md` in this folder.
