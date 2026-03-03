"""
LinkedIn Content Calendar Generator

This tool generates a weekly/monthly content calendar based on your LinkedIn strategy.

Usage:
    python linkedin_calendar_generator.py
    python linkedin_calendar_generator.py --weeks 4 --start-date 2026-02-17
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path


# Weekly posting schedule from strategy
WEEKLY_SCHEDULE = {
    "Monday": {
        "time": "09:00",
        "pillar": "educational",
        "format": "Carousel post or long-form article",
        "topic_type": "Industry insights, how-to guides",
        "cta": "Save this for later"
    },
    "Tuesday": {
        "time": "12:00",
        "pillar": "engagement",
        "format": "Question or poll",
        "topic_type": "Industry discussion, audience pain points",
        "cta": "Comment below"
    },
    "Wednesday": {
        "time": "10:00",
        "pillar": "social_proof",
        "format": "Case study or testimonial",
        "topic_type": "Client success story, results achieved",
        "cta": "Want similar results? DM me"
    },
    "Thursday": {
        "time": "14:00",
        "pillar": "educational",
        "format": "Video or infographic",
        "topic_type": "Quick tips, best practices",
        "cta": "Follow for more tips"
    },
    "Friday": {
        "time": "11:00",
        "pillar": "engagement",
        "format": "Behind-the-scenes or personal story",
        "topic_type": "Lessons learned, industry observations",
        "cta": "What's your take?"
    }
}


def generate_calendar(start_date, weeks, business_type, target_audience, include_promotional=True):
    """Generate content calendar for specified weeks."""

    calendar = []
    current_date = start_date
    post_id = 1

    for week in range(weeks):
        week_number = week + 1

        # Generate posts for each day of the week
        for day_name, schedule in WEEKLY_SCHEDULE.items():
            # Calculate the date for this day
            days_ahead = list(WEEKLY_SCHEDULE.keys()).index(day_name)
            post_date = current_date + timedelta(days=days_ahead)

            # Create calendar entry
            entry = {
                "id": post_id,
                "week": week_number,
                "date": post_date.strftime("%Y-%m-%d"),
                "day": day_name,
                "time": schedule["time"],
                "datetime": f"{post_date.strftime('%Y-%m-%d')} {schedule['time']}",
                "pillar": schedule["pillar"],
                "format": schedule["format"],
                "topic_type": schedule["topic_type"],
                "cta": schedule["cta"],
                "status": "scheduled",
                "notes": ""
            }

            # Add topic suggestions based on pillar
            if schedule["pillar"] == "educational":
                entry["topic_suggestions"] = [
                    f"How {business_type} transforms {target_audience}",
                    f"Common mistakes {target_audience} make with automation",
                    f"The ROI of {business_type} for {target_audience}"
                ]
            elif schedule["pillar"] == "social_proof":
                entry["topic_suggestions"] = [
                    f"Case study: {target_audience} success story",
                    f"Before/after: Client transformation",
                    f"Real results: Metrics and ROI"
                ]
            elif schedule["pillar"] == "engagement":
                entry["topic_suggestions"] = [
                    f"What's your biggest challenge with automation?",
                    f"Hot take: Controversial industry opinion",
                    f"Behind the scenes: Our process"
                ]

            calendar.append(entry)
            post_id += 1

        # Add promotional post every 2 weeks (10% of content)
        if include_promotional and week % 2 == 1:
            promo_date = current_date + timedelta(days=5)  # Saturday
            promo_entry = {
                "id": post_id,
                "week": week_number,
                "date": promo_date.strftime("%Y-%m-%d"),
                "day": "Saturday",
                "time": "09:00",
                "datetime": f"{promo_date.strftime('%Y-%m-%d')} 09:00",
                "pillar": "promotional",
                "format": "Offer or resource",
                "topic_type": "Free resource, consultation offer, webinar",
                "cta": "DM to claim / Download link in comments",
                "status": "scheduled",
                "topic_suggestions": [
                    f"Free {business_type} audit for {target_audience}",
                    f"Download: ROI calculator",
                    f"Limited spots: Free consultation"
                ],
                "notes": "Keep promotional content soft and value-focused"
            }
            calendar.append(promo_entry)
            post_id += 1

        # Move to next week
        current_date += timedelta(weeks=1)

    return calendar


def generate_markdown_calendar(calendar, business_type, target_audience):
    """Generate markdown formatted calendar."""

    md = f"""# LinkedIn Content Calendar

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Business Type:** {business_type}
**Target Audience:** {target_audience}
**Total Posts:** {len(calendar)}

---

## Calendar Overview

"""

    # Group by week
    weeks = {}
    for entry in calendar:
        week = entry["week"]
        if week not in weeks:
            weeks[week] = []
        weeks[week].append(entry)

    # Generate week-by-week calendar
    for week_num in sorted(weeks.keys()):
        week_posts = weeks[week_num]
        md += f"\n### Week {week_num}\n\n"

        for post in week_posts:
            md += f"""#### {post['day']}, {post['date']} at {post['time']}

**Pillar:** {post['pillar'].replace('_', ' ').title()}
**Format:** {post['format']}
**Topic Type:** {post['topic_type']}
**CTA:** {post['cta']}

**Topic Suggestions:**
"""
            for suggestion in post.get('topic_suggestions', []):
                md += f"- {suggestion}\n"

            md += f"\n**Status:** {post['status']}\n"
            if post.get('notes'):
                md += f"**Notes:** {post['notes']}\n"
            md += "\n---\n\n"

    # Add implementation checklist
    md += """
## Implementation Checklist

### Before You Start
- [ ] Review all scheduled posts
- [ ] Customize topic suggestions for your brand
- [ ] Prepare any required assets (images, videos, carousels)
- [ ] Set up scheduling tool (LinkedIn native, Buffer, or Hootsuite)

### Weekly Routine
- [ ] Monday: Review week's calendar
- [ ] Daily: Engage with 10 target posts
- [ ] Daily: Respond to all comments within 24 hours
- [ ] Friday: Prepare next week's content
- [ ] Sunday: Schedule next week's posts

### Monthly Review
- [ ] Analyze top-performing posts
- [ ] Adjust content mix based on engagement
- [ ] Update topic suggestions
- [ ] Refine target audience

---

## Content Pillar Distribution

Based on your calendar:
- **Educational:** 40% (2 posts/week)
- **Engagement:** 40% (2 posts/week)
- **Social Proof:** 20% (1 post/week)
- **Promotional:** 10% (1 post every 2 weeks)

---

## Best Practices

### Timing
- Post during business hours (9 AM - 5 PM)
- Avoid weekends unless testing
- Be consistent with posting times

### Engagement
- Respond to comments within first hour
- Engage with target audience's posts daily
- Use relevant hashtags (3-5 per post)

### Content Quality
- Hook in first line (grab attention)
- Use line breaks for readability
- Include clear CTA
- Add value in every post

---

*This calendar is based on your LinkedIn Content Strategy. Adjust as needed based on your results and audience feedback.*
"""

    return md


def save_calendar(calendar, output_file="content_calendar.json"):
    """Save calendar to JSON file."""
    output_path = Path(output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate LinkedIn content calendar'
    )
    parser.add_argument(
        '--weeks',
        type=int,
        default=4,
        help='Number of weeks to generate (default: 4)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date (YYYY-MM-DD, default: next Monday)'
    )
    parser.add_argument(
        '--business',
        type=str,
        default='AI automation consulting',
        help='Your business type'
    )
    parser.add_argument(
        '--target',
        type=str,
        default='small businesses',
        help='Target audience'
    )
    parser.add_argument(
        '--no-promotional',
        action='store_true',
        help='Exclude promotional posts'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='content_calendar',
        help='Output file name (without extension)'
    )

    args = parser.parse_args()

    print("="*70)
    print("LinkedIn Content Calendar Generator")
    print("="*70)
    print()

    # Determine start date
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        # Default to next Monday
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        start_date = today + timedelta(days=days_ahead)

    print(f"Start Date: {start_date.strftime('%Y-%m-%d')} ({start_date.strftime('%A')})")
    print(f"Duration: {args.weeks} weeks")
    print(f"Business: {args.business}")
    print(f"Target: {args.target}")
    print()

    # Generate calendar
    print("Generating content calendar...")
    calendar = generate_calendar(
        start_date=start_date,
        weeks=args.weeks,
        business_type=args.business,
        target_audience=args.target,
        include_promotional=not args.no_promotional
    )

    # Save JSON
    json_path = save_calendar(calendar, f"{args.output}.json")
    print(f"[SUCCESS] JSON calendar saved to: {json_path.absolute()}")

    # Generate and save markdown
    md_content = generate_markdown_calendar(calendar, args.business, args.target)
    md_path = Path(f"{args.output}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"[SUCCESS] Markdown calendar saved to: {md_path.absolute()}")

    print()
    print(f"[COUNT] Total posts scheduled: {len(calendar)}")
    print()
    print("Next steps:")
    print("1. Review the calendar in", f"{args.output}.md")
    print("2. Customize topic suggestions")
    print("3. Use linkedin_post_generator.py to create posts")
    print("4. Schedule posts in your preferred tool")


if __name__ == "__main__":
    main()
