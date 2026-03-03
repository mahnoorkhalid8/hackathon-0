"""
WhatsApp View Contacts Script

This script displays and searches WhatsApp contacts with export options.

Usage:
    python view_contacts.py
    python view_contacts.py --search "john"
    python view_contacts.py --export json --output contacts.json
"""

import sys
import os
import json
import csv
import argparse
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'whatsapp-node'))


def get_contacts():
    """Fetch contacts from WhatsApp backend."""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/contacts", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('contacts', [])
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []


def search_contacts(contacts, query):
    """Filter contacts by search query."""
    if not query:
        return contacts

    query_lower = query.lower()
    return [c for c in contacts if query_lower in c.get('name', '').lower()]


def display_contacts(contacts, limit=None):
    """Display contacts in a formatted table."""
    if not contacts:
        print("No contacts found.")
        return

    display_list = contacts[:limit] if limit else contacts

    print("\n" + "="*70)
    print(f"{'#':<5} {'Name':<30} {'Number':<20} {'In Contacts'}")
    print("="*70)

    for i, contact in enumerate(display_list, 1):
        name = contact.get('name', 'Unknown')[:28]
        number = contact.get('number', 'N/A')
        in_contacts = "Yes" if contact.get('isMyContact') else "No"
        print(f"{i:<5} {name:<30} {number:<20} {in_contacts}")

    print("="*70)
    print(f"Total: {len(contacts)} contacts")
    if limit and len(contacts) > limit:
        print(f"Showing first {limit} contacts")


def export_json(contacts, output_file):
    """Export contacts to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(contacts)} contacts to {output_file}")


def export_csv(contacts, output_file):
    """Export contacts to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'number', 'isMyContact'])
        writer.writeheader()
        for contact in contacts:
            writer.writerow({
                'name': contact.get('name', 'Unknown'),
                'number': contact.get('number', 'N/A'),
                'isMyContact': contact.get('isMyContact', False)
            })
    print(f"Exported {len(contacts)} contacts to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='View WhatsApp contacts')
    parser.add_argument('--search', type=str, help='Search contacts by name')
    parser.add_argument('--limit', type=int, help='Limit number of contacts to display')
    parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    print("="*70)
    print("WhatsApp View Contacts - Skills Interface")
    print("="*70)
    print()

    # Fetch contacts
    print("Loading contacts...")
    contacts = get_contacts()

    if not contacts:
        print("No contacts found. Make sure Node.js backend is running.")
        return

    # Search if query provided
    if args.search:
        contacts = search_contacts(contacts, args.search)
        print(f"Found {len(contacts)} matching contacts")

    # Display contacts
    display_contacts(contacts, args.limit)

    # Export if requested
    if args.export and args.output:
        if args.export == 'json':
            export_json(contacts, args.output)
        elif args.export == 'csv':
            export_csv(contacts, args.output)


if __name__ == "__main__":
    main()
