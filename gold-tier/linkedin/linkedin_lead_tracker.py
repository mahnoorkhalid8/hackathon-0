"""
LinkedIn Lead Tracker

This tool helps track and manage leads generated from LinkedIn content strategy.

Usage:
    python linkedin_lead_tracker.py
    python linkedin_lead_tracker.py --action add
    python linkedin_lead_tracker.py --action list --status all
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


LEAD_STAGES = ["new", "contacted", "qualified", "consultation", "proposal", "won", "lost"]
LEAD_SOURCES = ["dm", "comment", "profile_view", "connection_request", "post_engagement", "other"]


def load_leads(file_path="leads.json"):
    """Load leads from JSON file."""
    path = Path(file_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"leads": [], "stats": {}}


def save_leads(data, file_path="leads.json"):
    """Save leads to JSON file."""
    path = Path(file_path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def add_lead(data):
    """Add a new lead interactively."""
    print("\n" + "="*70)
    print("Add New Lead")
    print("="*70)
    print()

    # Get lead information
    name = input("Lead Name: ").strip()
    if not name:
        print("[ERROR] Name is required")
        return data

    company = input("Company (optional): ").strip()

    print("\nLead Source:")
    for i, source in enumerate(LEAD_SOURCES, 1):
        print(f"  {i}. {source}")
    source_choice = input("Select source (1-6): ").strip()
    try:
        source = LEAD_SOURCES[int(source_choice) - 1]
    except (ValueError, IndexError):
        source = "other"

    linkedin_url = input("LinkedIn Profile URL (optional): ").strip()
    email = input("Email (optional): ").strip()
    phone = input("Phone (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    # Create lead entry
    lead_id = len(data["leads"]) + 1
    lead = {
        "id": lead_id,
        "name": name,
        "company": company,
        "source": source,
        "stage": "new",
        "linkedin_url": linkedin_url,
        "email": email,
        "phone": phone,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "interactions": [],
        "value": 0,
        "status": "active"
    }

    data["leads"].append(lead)
    print(f"\n[SUCCESS] Lead #{lead_id} added: {name}")

    return data


def list_leads(data, status_filter="active", stage_filter=None):
    """List all leads with optional filters."""
    leads = data["leads"]

    # Apply filters
    if status_filter != "all":
        leads = [l for l in leads if l.get("status") == status_filter]

    if stage_filter:
        leads = [l for l in leads if l.get("stage") == stage_filter]

    if not leads:
        print("\nNo leads found matching criteria.")
        return

    print("\n" + "="*70)
    print(f"{'ID':<5} {'Name':<20} {'Company':<20} {'Stage':<15} {'Source'}")
    print("="*70)

    for lead in leads:
        lead_id = str(lead.get("id", ""))[:4]
        name = lead.get("name", "Unknown")[:18]
        company = lead.get("company", "")[:18]
        stage = lead.get("stage", "new")[:13]
        source = lead.get("source", "")[:15]

        print(f"{lead_id:<5} {name:<20} {company:<20} {stage:<15} {source}")

    print("="*70)
    print(f"Total: {len(leads)} leads")


def view_lead(data, lead_id):
    """View detailed information about a lead."""
    lead = next((l for l in data["leads"] if l["id"] == lead_id), None)

    if not lead:
        print(f"[ERROR] Lead #{lead_id} not found")
        return

    print("\n" + "="*70)
    print(f"Lead #{lead['id']}: {lead['name']}")
    print("="*70)
    print()
    print(f"Company: {lead.get('company', 'N/A')}")
    print(f"Stage: {lead.get('stage', 'new')}")
    print(f"Source: {lead.get('source', 'N/A')}")
    print(f"Status: {lead.get('status', 'active')}")
    print()
    print(f"LinkedIn: {lead.get('linkedin_url', 'N/A')}")
    print(f"Email: {lead.get('email', 'N/A')}")
    print(f"Phone: {lead.get('phone', 'N/A')}")
    print()
    print(f"Created: {lead.get('created_at', 'N/A')}")
    print(f"Updated: {lead.get('updated_at', 'N/A')}")
    print()
    print(f"Estimated Value: ${lead.get('value', 0)}")
    print()
    print(f"Notes: {lead.get('notes', 'None')}")
    print()

    # Show interactions
    interactions = lead.get("interactions", [])
    if interactions:
        print("Interactions:")
        for i, interaction in enumerate(interactions, 1):
            print(f"  {i}. [{interaction.get('date', 'N/A')}] {interaction.get('type', 'N/A')}")
            print(f"     {interaction.get('notes', '')}")
    else:
        print("Interactions: None")


def update_lead_stage(data, lead_id, new_stage):
    """Update lead stage."""
    lead = next((l for l in data["leads"] if l["id"] == lead_id), None)

    if not lead:
        print(f"[ERROR] Lead #{lead_id} not found")
        return data

    old_stage = lead.get("stage", "new")
    lead["stage"] = new_stage
    lead["updated_at"] = datetime.now().isoformat()

    # Add interaction
    interaction = {
        "date": datetime.now().isoformat(),
        "type": "stage_change",
        "notes": f"Stage changed from {old_stage} to {new_stage}"
    }
    lead.setdefault("interactions", []).append(interaction)

    print(f"[SUCCESS] Lead #{lead_id} stage updated: {old_stage} -> {new_stage}")

    return data


def add_interaction(data, lead_id):
    """Add an interaction to a lead."""
    lead = next((l for l in data["leads"] if l["id"] == lead_id), None)

    if not lead:
        print(f"[ERROR] Lead #{lead_id} not found")
        return data

    print(f"\nAdd Interaction for Lead #{lead_id}: {lead['name']}")
    print()

    interaction_type = input("Type (call/email/meeting/dm/other): ").strip()
    notes = input("Notes: ").strip()

    interaction = {
        "date": datetime.now().isoformat(),
        "type": interaction_type,
        "notes": notes
    }

    lead.setdefault("interactions", []).append(interaction)
    lead["updated_at"] = datetime.now().isoformat()

    print(f"[SUCCESS] Interaction added to lead #{lead_id}")

    return data


def generate_stats(data):
    """Generate statistics from leads data."""
    leads = data["leads"]

    if not leads:
        print("\nNo leads to analyze.")
        return

    # Calculate stats
    total_leads = len(leads)
    active_leads = len([l for l in leads if l.get("status") == "active"])
    won_leads = len([l for l in leads if l.get("stage") == "won"])
    lost_leads = len([l for l in leads if l.get("stage") == "lost"])

    # Stage distribution
    stage_counts = {}
    for lead in leads:
        stage = lead.get("stage", "new")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    # Source distribution
    source_counts = {}
    for lead in leads:
        source = lead.get("source", "other")
        source_counts[source] = source_counts.get(source, 0) + 1

    # Total value
    total_value = sum(l.get("value", 0) for l in leads if l.get("stage") == "won")
    potential_value = sum(l.get("value", 0) for l in leads if l.get("status") == "active")

    # Conversion rate
    conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0

    # Print stats
    print("\n" + "="*70)
    print("Lead Statistics")
    print("="*70)
    print()
    print(f"Total Leads: {total_leads}")
    print(f"Active Leads: {active_leads}")
    print(f"Won: {won_leads}")
    print(f"Lost: {lost_leads}")
    print(f"Conversion Rate: {conversion_rate:.1f}%")
    print()
    print(f"Total Revenue (Won): ${total_value:,.2f}")
    print(f"Potential Revenue (Active): ${potential_value:,.2f}")
    print()

    print("Leads by Stage:")
    for stage, count in sorted(stage_counts.items()):
        percentage = (count / total_leads * 100) if total_leads > 0 else 0
        print(f"  {stage:<15} {count:>3} ({percentage:>5.1f}%)")

    print()
    print("Leads by Source:")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_leads * 100) if total_leads > 0 else 0
        print(f"  {source:<20} {count:>3} ({percentage:>5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Lead Tracker')
    parser.add_argument(
        '--action',
        type=str,
        choices=['add', 'list', 'view', 'update', 'interact', 'stats'],
        default='list',
        help='Action to perform'
    )
    parser.add_argument('--id', type=int, help='Lead ID')
    parser.add_argument('--stage', type=str, choices=LEAD_STAGES, help='Lead stage')
    parser.add_argument('--status', type=str, default='active', help='Filter by status')
    parser.add_argument('--file', type=str, default='leads.json', help='Data file')

    args = parser.parse_args()

    print("="*70)
    print("LinkedIn Lead Tracker")
    print("="*70)

    # Load data
    data = load_leads(args.file)

    # Perform action
    if args.action == 'add':
        data = add_lead(data)
        save_leads(data, args.file)

    elif args.action == 'list':
        list_leads(data, status_filter=args.status, stage_filter=args.stage)

    elif args.action == 'view':
        if not args.id:
            print("[ERROR] --id is required for view action")
        else:
            view_lead(data, args.id)

    elif args.action == 'update':
        if not args.id or not args.stage:
            print("[ERROR] --id and --stage are required for update action")
        else:
            data = update_lead_stage(data, args.id, args.stage)
            save_leads(data, args.file)

    elif args.action == 'interact':
        if not args.id:
            print("[ERROR] --id is required for interact action")
        else:
            data = add_interaction(data, args.id)
            save_leads(data, args.file)

    elif args.action == 'stats':
        generate_stats(data)


if __name__ == "__main__":
    main()
