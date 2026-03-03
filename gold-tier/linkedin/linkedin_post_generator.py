"""
LinkedIn Post Generator

This tool generates LinkedIn posts based on your content strategy and pillars.

Usage:
    python linkedin_post_generator.py
    python linkedin_post_generator.py --pillar educational --topic "AI automation benefits"
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


# Post templates by pillar
POST_TEMPLATES = {
    "educational": [
        {
            "hook": "Here's what most {target_audience} get wrong about {topic}:",
            "structure": "hook + 3-5 bullet points + cta",
            "cta": "Save this for later 💾"
        },
        {
            "hook": "The {number}-step framework for {desired_outcome}:",
            "structure": "hook + numbered steps + cta",
            "cta": "Follow for more {topic} tips"
        },
        {
            "hook": "Why {common_belief} is costing you {negative_outcome}:",
            "structure": "hook + problem + solution + cta",
            "cta": "Share with someone who needs this"
        }
    ],
    "social_proof": [
        {
            "hook": "How we helped {client_type} achieve {result} in {timeframe}:",
            "structure": "hook + before/after + key metrics + cta",
            "cta": "Want similar results? DM me"
        },
        {
            "hook": "Real results: {metric} improvement for {client_type}",
            "structure": "hook + case study + roi + cta",
            "cta": "Book a free consultation (link in profile)"
        }
    ],
    "engagement": [
        {
            "hook": "What's your biggest challenge with {topic}?",
            "structure": "question + context + invitation",
            "cta": "Comment below 👇"
        },
        {
            "hook": "Hot take: {controversial_opinion}",
            "structure": "opinion + reasoning + question",
            "cta": "Agree or disagree?"
        }
    ],
    "promotional": [
        {
            "hook": "Free resource: {resource_name} for {target_audience}",
            "structure": "hook + benefits + how to get it",
            "cta": "Download link in comments"
        },
        {
            "hook": "Limited spots: {offer} for {target_audience}",
            "structure": "hook + value prop + urgency + cta",
            "cta": "DM 'INTERESTED' to claim yours"
        }
    ]
}


def generate_educational_post(topic, target_audience, business_type):
    """Generate an educational post."""

    posts = [
        f"""Here's what most {target_audience} get wrong about {topic}:

❌ They think it's too expensive
❌ They believe it's only for large companies
❌ They assume it requires technical expertise

The truth?

✅ {topic} pays for itself within 3-6 months
✅ Small businesses see the biggest ROI
✅ Modern solutions are plug-and-play

The companies that embrace {topic} early gain a massive competitive advantage.

The ones that wait? They're left playing catch-up.

💾 Save this for later""",

        f"""The 5-step framework for implementing {topic} in your business:

1️⃣ Identify repetitive tasks (start with the most time-consuming)
2️⃣ Calculate current cost (time × hourly rate)
3️⃣ Research solutions (compare 3-5 options)
4️⃣ Start small (pilot with one process)
5️⃣ Measure & scale (track ROI, expand what works)

Most {target_audience} skip step 2 and wonder why they can't justify the investment.

Don't make that mistake.

Follow for more {business_type} tips 🚀""",

        f"""Why waiting to adopt {topic} is costing you more than you think:

Every day without {topic}:
• Your team wastes 2-3 hours on manual tasks
• You miss opportunities competitors are capturing
• Your costs stay high while margins shrink

The real cost isn't the investment.

It's the opportunity cost of NOT investing.

I've seen {target_audience} increase productivity by 40% within 60 days of implementation.

The question isn't "Can we afford it?"

It's "Can we afford NOT to?"

Share with someone who needs to hear this 📢"""
    ]

    return posts


def generate_social_proof_post(business_type, target_audience):
    """Generate a social proof post."""

    posts = [
        f"""How we helped a {target_audience} achieve 10x ROI in 90 days:

BEFORE:
• 20 hours/week on manual data entry
• Frequent errors and delays
• Team burnout and turnover

AFTER:
• 2 hours/week (90% time saved)
• Zero errors, instant processing
• Team focused on growth activities

THE RESULT:
• $8,000/month saved in labor costs
• 10x ROI in first quarter
• Team morale through the roof

This is what's possible when you implement the right {business_type} solution.

Want similar results? DM me 📩""",

        f"""Real numbers from a recent {target_audience} client:

📊 METRICS:
• 85% reduction in processing time
• $12,000 monthly cost savings
• 3.2 month payback period
• 400% annual ROI

💡 THE SOLUTION:
We automated their invoice processing, customer onboarding, and reporting workflows.

⏱️ THE TIMELINE:
• Week 1-2: Assessment & planning
• Week 3-4: Implementation
• Week 5-8: Training & optimization
• Month 3+: Full ROI realized

This isn't a special case.

This is what happens when {target_audience} stop doing things manually and start working smart.

Book a free consultation (link in profile) 🔗"""
    ]

    return posts


def generate_engagement_post(topic, target_audience):
    """Generate an engagement post."""

    posts = [
        f"""What's your biggest challenge with {topic}?

I'm seeing {target_audience} struggle with:

A) Finding the right solution
B) Getting team buy-in
C) Measuring ROI
D) Implementation complexity

Comment A, B, C, or D below 👇

(And I'll share specific advice for your situation)""",

        f"""Hot take: Most {target_audience} are wasting money on {topic} because they're solving the wrong problem.

They automate tasks that should be eliminated.

They optimize processes that should be redesigned.

They buy expensive tools when simple solutions would work.

The result? Expensive automation that doesn't move the needle.

Before you automate, ask:
1. Should we be doing this at all?
2. Can we simplify it first?
3. What's the actual business impact?

Agree or disagree? 🤔"""
    ]

    return posts


def generate_promotional_post(business_type, target_audience):
    """Generate a promotional post."""

    posts = [
        f"""Free Download: The {business_type} ROI Calculator for {target_audience}

Calculate exactly how much you're losing to manual processes.

✅ Input your current workflows
✅ See time & cost savings
✅ Get ROI projections
✅ Identify quick wins

No email required. No sales pitch.

Just a practical tool to help you make informed decisions.

Download link in comments 👇""",

        f"""Limited spots: Free {business_type} audit for {target_audience}

I'm offering 5 free audits this week to help {target_audience} identify automation opportunities.

What you get:
✅ 30-minute consultation
✅ Process analysis
✅ ROI estimate
✅ Implementation roadmap

Worth $500. Free this week only.

Why? I'm building case studies and need 5 businesses to work with.

DM 'AUDIT' if you want one of the 5 spots 📩

First come, first served."""
    ]

    return posts


def save_posts(posts, output_file="generated_posts.json"):
    """Save generated posts to JSON file."""
    output_path = Path(output_file)

    # Load existing posts if file exists
    existing_posts = []
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_posts = json.load(f)

    # Add new posts
    existing_posts.extend(posts)

    # Save all posts
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_posts, f, indent=2, ensure_ascii=False)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate LinkedIn posts based on content strategy'
    )
    parser.add_argument(
        '--pillar',
        type=str,
        choices=['educational', 'social_proof', 'engagement', 'promotional', 'all'],
        default='all',
        help='Content pillar to generate posts for'
    )
    parser.add_argument(
        '--topic',
        type=str,
        default='AI automation',
        help='Main topic for the posts'
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
        '--count',
        type=int,
        default=3,
        help='Number of posts to generate per pillar'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='generated_posts.json',
        help='Output file name'
    )

    args = parser.parse_args()

    print("="*70)
    print("LinkedIn Post Generator")
    print("="*70)
    print()
    print(f"Topic: {args.topic}")
    print(f"Business: {args.business}")
    print(f"Target: {args.target}")
    print(f"Pillar: {args.pillar}")
    print()

    all_posts = []

    # Generate posts based on pillar
    if args.pillar in ['educational', 'all']:
        print("Generating educational posts...")
        posts = generate_educational_post(args.topic, args.target, args.business)
        for i, post in enumerate(posts[:args.count], 1):
            all_posts.append({
                "id": len(all_posts) + 1,
                "pillar": "educational",
                "topic": args.topic,
                "content": post,
                "generated_at": datetime.now().isoformat(),
                "status": "draft"
            })
        print(f"  Generated {len(posts[:args.count])} educational posts")

    if args.pillar in ['social_proof', 'all']:
        print("Generating social proof posts...")
        posts = generate_social_proof_post(args.business, args.target)
        for i, post in enumerate(posts[:args.count], 1):
            all_posts.append({
                "id": len(all_posts) + 1,
                "pillar": "social_proof",
                "topic": args.topic,
                "content": post,
                "generated_at": datetime.now().isoformat(),
                "status": "draft"
            })
        print(f"  Generated {len(posts[:args.count])} social proof posts")

    if args.pillar in ['engagement', 'all']:
        print("Generating engagement posts...")
        posts = generate_engagement_post(args.topic, args.target)
        for i, post in enumerate(posts[:args.count], 1):
            all_posts.append({
                "id": len(all_posts) + 1,
                "pillar": "engagement",
                "topic": args.topic,
                "content": post,
                "generated_at": datetime.now().isoformat(),
                "status": "draft"
            })
        print(f"  Generated {len(posts[:args.count])} engagement posts")

    if args.pillar in ['promotional', 'all']:
        print("Generating promotional posts...")
        posts = generate_promotional_post(args.business, args.target)
        for i, post in enumerate(posts[:args.count], 1):
            all_posts.append({
                "id": len(all_posts) + 1,
                "pillar": "promotional",
                "topic": args.topic,
                "content": post,
                "generated_at": datetime.now().isoformat(),
                "status": "draft"
            })
        print(f"  Generated {len(posts[:args.count])} promotional posts")

    # Save posts
    output_path = save_posts(all_posts, args.output)

    print()
    print("[SUCCESS] Posts generated successfully!")
    print(f"[FILE] Saved to: {output_path.absolute()}")
    print(f"[COUNT] Total posts: {len(all_posts)}")
    print()
    print("Next steps:")
    print("1. Review generated posts in", args.output)
    print("2. Customize posts for your brand voice")
    print("3. Schedule posts according to your content calendar")
    print("4. Track engagement and optimize")


if __name__ == "__main__":
    main()
