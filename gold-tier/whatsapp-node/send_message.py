"""
Simple WhatsApp Message Sender - Contact Name Based

This script provides a simple command-line interface to send WhatsApp messages
by selecting contacts by name instead of typing phone numbers.

Usage:
    python send_message.py
"""

import requests
from datetime import datetime


def get_account_info():
    """Get authenticated WhatsApp account information."""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/info", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: Cannot connect to WhatsApp backend")
        print(f"Make sure Node.js server is running (npm start)")
        return None


def get_contacts():
    """Get list of WhatsApp contacts."""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/contacts", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('contacts', [])
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []


def search_contacts(contacts, query):
    """
    Search contacts by name.

    Args:
        contacts: List of contact dictionaries
        query: Search query string

    Returns:
        list: Filtered contacts matching the query
    """
    if not query:
        return contacts

    query_lower = query.lower()
    return [
        contact for contact in contacts
        if query_lower in contact.get('name', '').lower()
    ]


def display_contacts(contacts, start=0, limit=10):
    """
    Display a paginated list of contacts.

    Args:
        contacts: List of contacts to display
        start: Starting index
        limit: Number of contacts to show

    Returns:
        tuple: (displayed_contacts, has_more)
    """
    end = min(start + limit, len(contacts))
    displayed = contacts[start:end]

    print("\n" + "="*70)
    print("CONTACTS")
    print("="*70)

    for i, contact in enumerate(displayed, start=start+1):
        name = contact.get('name', 'Unknown')
        number = contact.get('number', 'N/A')
        print(f"{i:3d}. {name:<40} ({number})")

    print("="*70)

    has_more = end < len(contacts)
    if has_more:
        print(f"Showing {start+1}-{end} of {len(contacts)} contacts")
    else:
        print(f"Total: {len(contacts)} contacts")

    return displayed, has_more


def select_contact(contacts):
    """
    Interactive contact selection.

    Args:
        contacts: List of all contacts

    Returns:
        dict: Selected contact or None
    """
    if not contacts:
        print("\n[ERROR] No contacts found")
        print("Make sure you have recent WhatsApp conversations")
        return None

    current_page = 0
    page_size = 10
    filtered_contacts = contacts

    while True:
        # Display current page
        displayed, has_more = display_contacts(
            filtered_contacts,
            start=current_page * page_size,
            limit=page_size
        )

        print("\nOptions:")
        print("  - Enter contact number (1-{}) to select".format(len(filtered_contacts)))
        print("  - Type 's' to search by name")
        print("  - Type 'n' for next page" + (" (more contacts available)" if has_more else ""))
        print("  - Type 'p' for previous page")
        print("  - Type 'c' to cancel")
        print()

        choice = input("Your choice: ").strip().lower()

        # Cancel
        if choice == 'c':
            return None

        # Search
        if choice == 's':
            query = input("\nEnter name to search: ").strip()
            filtered_contacts = search_contacts(contacts, query)

            if not filtered_contacts:
                print(f"\n[ERROR] No contacts found matching '{query}'")
                filtered_contacts = contacts
            else:
                print(f"\n[OK] Found {len(filtered_contacts)} contact(s)")

            current_page = 0
            continue

        # Next page
        if choice == 'n':
            if has_more:
                current_page += 1
            else:
                print("\n[INFO] Already on last page")
            continue

        # Previous page
        if choice == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                print("\n[INFO] Already on first page")
            continue

        # Select by number
        try:
            selection = int(choice)
            if 1 <= selection <= len(filtered_contacts):
                selected = filtered_contacts[selection - 1]
                print(f"\n[OK] Selected: {selected.get('name')} ({selected.get('number')})")
                return selected
            else:
                print(f"\n[ERROR] Invalid number. Choose 1-{len(filtered_contacts)}")
        except ValueError:
            print("\n[ERROR] Invalid input. Please try again.")


def send_message(recipient, message):
    """
    Send a WhatsApp message.

    Args:
        recipient: Phone number with country code
        message: Message text to send

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        response = requests.post(
            "http://localhost:3000/api/whatsapp/send",
            json={"number": recipient, "message": message},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            print(f"\n[SUCCESS] Message sent!")
            print(f"Message ID: {result.get('messageId')}")
            print(f"Timestamp: {datetime.fromtimestamp(result.get('timestamp'))}")
            return True
        else:
            print(f"\n[ERROR] Failed to send: {result.get('error', 'Unknown error')}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def main():
    """Main CLI interface."""
    print("="*70)
    print("WhatsApp Message Sender - Contact Name Based")
    print("="*70)
    print()

    # Check connection
    print("Checking WhatsApp connection...")
    account = get_account_info()

    if not account:
        print("\n[ERROR] Cannot connect to WhatsApp backend")
        print("Please make sure:")
        print("  1. Node.js server is running (npm start)")
        print("  2. WhatsApp is authenticated")
        return

    print(f"[OK] Connected as: {account.get('name')} ({account.get('number')})")
    print()

    # Load contacts
    print("Loading contacts...")
    contacts = get_contacts()

    if not contacts:
        print("\n[ERROR] Could not load contacts")
        print("Make sure you have recent WhatsApp conversations")
        return

    print(f"[OK] Loaded {len(contacts)} contacts")
    print()
    print("="*70)
    print()

    # Main loop
    while True:
        print("\nOptions:")
        print("  1. Send a message")
        print("  2. Reload contacts")
        print("  3. Exit")
        print()

        choice = input("Choose option (1, 2, or 3): ").strip()

        if choice == "3":
            print("\nGoodbye!")
            break

        if choice == "2":
            print("\nReloading contacts...")
            contacts = get_contacts()
            if contacts:
                print(f"[OK] Loaded {len(contacts)} contacts")
            else:
                print("[ERROR] Could not reload contacts")
            continue

        if choice != "1":
            print("\n[ERROR] Invalid option. Please choose 1, 2, or 3.")
            continue

        print("\n" + "-"*70)
        print("SEND MESSAGE")
        print("-"*70)

        # Select contact
        print("\nSelect a contact:")
        selected_contact = select_contact(contacts)

        if not selected_contact:
            print("\n[CANCELLED] No contact selected")
            continue

        recipient_name = selected_contact.get('name')
        recipient_number = selected_contact.get('number')

        # Get message
        print("\n" + "-"*70)
        print(f"Sending to: {recipient_name}")
        print("-"*70)
        print("\nEnter your message:")
        print("(Type your message and press Enter)")
        print()

        message = input("Message: ").strip()

        if not message:
            print("\n[ERROR] Message cannot be empty")
            continue

        # Confirm
        print("\n" + "="*70)
        print("CONFIRM")
        print("="*70)
        print(f"To:      {recipient_name} ({recipient_number})")
        print(f"Message: {message}")
        print("="*70)

        confirm = input("\nSend this message? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y']:
            print("\nSending message...")
            success = send_message(recipient_number, message)

            if success:
                print("\n[OK] Message sent successfully!")
            else:
                print("\n[FAILED] Could not send message")
        else:
            print("\n[CANCELLED] Message not sent")

        print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
