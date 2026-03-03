"""
Gmail Watcher Service for Silver Tier Digital FTE
Monitors Gmail inbox and saves unread emails as Markdown files.

Features:
- Checks unread emails every 2 minutes
- Saves emails to vault/Inbox/ as Markdown
- Logs sender, subject, timestamp
- Triggers agent_loop.py via file watcher integration
- OAuth2 authentication
- Comprehensive error handling
"""

import os
import sys
import time
import base64
import logging
import pickle
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class GmailWatcherConfig:
    """Configuration for Gmail watcher service."""

    # Paths
    inbox_path: str = "vault/Inbox"
    credentials_file: str = "config/gmail_credentials.json"
    token_file: str = "config/gmail_token.pickle"
    log_dir: str = "logs"

    # Gmail settings
    check_interval: int = 120  # 2 minutes in seconds
    max_results: int = 10  # Max emails to fetch per check
    mark_as_read: bool = False  # Whether to mark emails as read after processing

    # Scopes
    scopes: List[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(config: GmailWatcherConfig) -> logging.Logger:
    """Configure logging for Gmail watcher."""
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("GmailWatcher")
    logger.setLevel(getattr(logging, config.log_level))
    logger.handlers.clear()

    # File handler
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_dir / "gmail_watcher.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(config.log_format))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# GMAIL CLIENT
# ============================================================================

class GmailClient:
    """Handles Gmail API authentication and operations."""

    def __init__(self, config: GmailWatcherConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.service = None
        self.credentials = None

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            True if authentication successful
        """
        try:
            creds = None
            token_file = Path(self.config.token_file)
            credentials_file = Path(self.config.credentials_file)

            # Load existing token (JSON format)
            if token_file.exists():
                self.logger.info("Loading existing credentials...")
                creds = Credentials.from_authorized_user_file(
                    str(token_file),
                    self.config.scopes
                )

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    if not credentials_file.exists():
                        self.logger.error(f"Credentials file not found: {credentials_file}")
                        self.logger.error("Please download credentials from Google Cloud Console")
                        return False

                    self.logger.info("Starting OAuth2 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_file),
                        self.config.scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials (JSON format)
                self.logger.info("Saving credentials...")
                token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())

            # Build service
            self.credentials = creds
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Gmail API authentication successful")

            return True

        except Exception as e:
            self.logger.error(f"Authentication failed: {e}", exc_info=True)
            return False

    def get_unread_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from Gmail.

        Returns:
            List of email dictionaries
        """
        try:
            # Query for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=self.config.max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                self.logger.debug("No unread emails found")
                return []

            self.logger.info(f"Found {len(messages)} unread email(s)")

            # Fetch full email details
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as e:
            self.logger.error(f"Error fetching emails: {e}", exc_info=True)
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return []

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific email.

        Args:
            message_id: Gmail message ID

        Returns:
            Email details dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = message['payload']['headers']
            header_dict = {h['name'].lower(): h['value'] for h in headers}

            # Extract body
            body = self._extract_body(message['payload'])

            # Parse date
            date_str = header_dict.get('date', '')
            try:
                email_date = parsedate_to_datetime(date_str)
            except:
                email_date = datetime.now()

            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId', ''),
                'sender': header_dict.get('from', 'Unknown'),
                'to': header_dict.get('to', ''),
                'subject': header_dict.get('subject', 'No Subject'),
                'date': email_date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }

            self.logger.debug(f"Fetched email: {email_data['subject']}")

            return email_data

        except Exception as e:
            self.logger.error(f"Error getting email details for {message_id}: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """
        Extract email body from payload.

        Args:
            payload: Email payload

        Returns:
            Email body text
        """
        body = ""

        if 'parts' in payload:
            # Multipart email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        # Fallback to HTML if no plain text
                        html_body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        body = self._html_to_text(html_body)
        else:
            # Simple email
            if 'data' in payload.get('body', {}):
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')

        return body.strip()

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text (simple version).

        Args:
            html: HTML content

        Returns:
            Plain text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        return text.strip()

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            self.logger.debug(f"Marked email {message_id} as read")
            return True

        except Exception as e:
            self.logger.error(f"Error marking email as read: {e}")
            return False


# ============================================================================
# EMAIL PROCESSOR
# ============================================================================

class EmailProcessor:
    """Processes emails and saves them as Markdown files."""

    def __init__(self, config: GmailWatcherConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.inbox_path = Path(config.inbox_path)
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.emails_processed = 0
        self.emails_saved = 0
        self.emails_failed = 0

    def process_email(self, email: Dict[str, Any]) -> bool:
        """
        Process an email and save as Markdown.

        Args:
            email: Email data dictionary

        Returns:
            True if processed successfully
        """
        try:
            self.emails_processed += 1

            # Log email details
            self.logger.info(f"Processing email:")
            self.logger.info(f"  From: {email['sender']}")
            self.logger.info(f"  Subject: {email['subject']}")
            self.logger.info(f"  Date: {email['date']}")

            # Generate filename
            filename = self._generate_filename(email)
            filepath = self.inbox_path / filename

            # Generate markdown content
            markdown = self._generate_markdown(email)

            # Save file
            filepath.write_text(markdown, encoding='utf-8')

            self.logger.info(f"Saved email to: {filepath}")
            self.emails_saved += 1

            return True

        except Exception as e:
            self.logger.error(f"Error processing email: {e}", exc_info=True)
            self.emails_failed += 1
            return False

    def _generate_filename(self, email: Dict[str, Any]) -> str:
        """
        Generate a safe filename for the email.

        Args:
            email: Email data

        Returns:
            Filename string
        """
        # Extract sender name
        sender = email['sender']
        sender_match = re.search(r'([^<]+)', sender)
        sender_name = sender_match.group(1).strip() if sender_match else 'unknown'

        # Clean sender name
        sender_clean = re.sub(r'[^\w\s-]', '', sender_name)
        sender_clean = re.sub(r'[-\s]+', '-', sender_clean)
        sender_clean = sender_clean[:30]  # Limit length

        # Clean subject
        subject = email['subject']
        subject_clean = re.sub(r'[^\w\s-]', '', subject)
        subject_clean = re.sub(r'[-\s]+', '-', subject_clean)
        subject_clean = subject_clean[:50]  # Limit length

        # Timestamp
        timestamp = email['date'].strftime('%Y%m%d-%H%M%S')

        # Combine
        filename = f"email-{timestamp}-{sender_clean}-{subject_clean}.md"
        filename = filename.lower()

        return filename

    def _generate_markdown(self, email: Dict[str, Any]) -> str:
        """
        Generate Markdown content from email.

        Args:
            email: Email data

        Returns:
            Markdown string
        """
        # Extract sender email
        sender_email = email['sender']
        sender_match = re.search(r'<([^>]+)>', sender_email)
        sender_addr = sender_match.group(1) if sender_match else sender_email

        # Build markdown
        lines = [
            f"# Email: {email['subject']}",
            "",
            "**Type:** email",
            "**Source:** gmail_watcher",
            f"**Priority:** MEDIUM",
            "",
            "---",
            "",
            "## Email Details",
            "",
            f"**From:** {email['sender']}",
            f"**To:** {email['to']}",
            f"**Date:** {email['date'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Subject:** {email['subject']}",
            "",
            "---",
            "",
            "## Message",
            "",
            email['body'],
            "",
            "---",
            "",
            "## Metadata",
            "",
            f"**Gmail ID:** {email['id']}",
            f"**Thread ID:** {email['thread_id']}",
            f"**Labels:** {', '.join(email['labels'])}",
            f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Suggested Actions",
            "",
            "- [ ] Read and understand the email",
            "- [ ] Determine if response is needed",
            "- [ ] Take appropriate action",
            ""
        ]

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            'processed': self.emails_processed,
            'saved': self.emails_saved,
            'failed': self.emails_failed
        }


# ============================================================================
# GMAIL WATCHER SERVICE
# ============================================================================

class GmailWatcherService:
    """Main Gmail watcher service."""

    def __init__(self, config: Optional[GmailWatcherConfig] = None):
        self.config = config or GmailWatcherConfig()
        self.logger = setup_logging(self.config)

        # Components
        self.gmail_client = GmailClient(self.config, self.logger)
        self.email_processor = EmailProcessor(self.config, self.logger)

        # State
        self.running = False
        self.start_time: Optional[datetime] = None
        self.check_count = 0

    def check_once(self) -> Dict[str, Any]:
        """Check for emails once and return results."""
        self.logger.info("Authenticating with Gmail API...")

        if not self.gmail_client.authenticate():
            self.logger.error("Authentication failed")
            return {"success": False, "error": "Authentication failed"}

        self.logger.info("Checking for unread emails...")

        try:
            # Get unread emails
            emails = self.gmail_client.get_unread_emails()

            if not emails:
                self.logger.info("No unread emails found")
                return {"success": True, "processed": 0, "message": "No unread emails"}

            # Process each email
            processed = 0
            for email in emails:
                success = self.email_processor.process_email(email)
                if success:
                    processed += 1
                    if self.config.mark_as_read:
                        self.gmail_client.mark_as_read(email['id'])

            self.logger.info(f"Processed {processed}/{len(emails)} email(s)")
            return {
                "success": True,
                "processed": processed,
                "total": len(emails),
                "message": f"Processed {processed} email(s)"
            }

        except Exception as e:
            self.logger.error(f"Error checking emails: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def start(self):
        """Start the Gmail watcher service."""
        self.logger.info("="*70)
        self.logger.info("  Starting Gmail Watcher Service")
        self.logger.info("="*70)

        # Authenticate
        self.logger.info("Authenticating with Gmail API...")
        if not self.gmail_client.authenticate():
            self.logger.error("Authentication failed. Cannot start service.")
            return

        self.logger.info(f"Monitoring Gmail inbox")
        self.logger.info(f"Check interval: {self.config.check_interval} seconds")
        self.logger.info(f"Saving to: {self.config.inbox_path}")
        self.logger.info(f"Mark as read: {self.config.mark_as_read}")
        self.logger.info("")

        self.running = True
        self.start_time = datetime.now()

        # Main loop
        try:
            while self.running:
                self._check_emails()

                # Wait for next check
                self.logger.debug(f"Waiting {self.config.check_interval}s until next check...")
                time.sleep(self.config.check_interval)

        except KeyboardInterrupt:
            self.logger.info("\nReceived interrupt signal")
            self.stop()

    def stop(self):
        """Stop the Gmail watcher service."""
        self.logger.info("")
        self.logger.info("Stopping Gmail watcher service...")

        self.running = False

        # Print statistics
        self._print_statistics()

        self.logger.info("Gmail watcher service stopped")

    def _check_emails(self):
        """Check for new unread emails."""
        self.check_count += 1

        self.logger.info(f"Check #{self.check_count}: Fetching unread emails...")

        try:
            # Get unread emails
            emails = self.gmail_client.get_unread_emails()

            if not emails:
                self.logger.info("No unread emails found")
                return

            # Process each email
            for email in emails:
                success = self.email_processor.process_email(email)

                if success and self.config.mark_as_read:
                    self.gmail_client.mark_as_read(email['id'])

            self.logger.info(f"Processed {len(emails)} email(s)")

        except Exception as e:
            self.logger.error(f"Error during email check: {e}", exc_info=True)

    def _print_statistics(self):
        """Print service statistics."""
        if not self.start_time:
            return

        uptime = datetime.now() - self.start_time
        stats = self.email_processor.get_stats()

        self.logger.info("")
        self.logger.info("="*70)
        self.logger.info("  Service Statistics")
        self.logger.info("="*70)
        self.logger.info(f"Uptime: {uptime}")
        self.logger.info(f"Checks performed: {self.check_count}")
        self.logger.info(f"Emails processed: {stats['processed']}")
        self.logger.info(f"Emails saved: {stats['saved']}")
        self.logger.info(f"Emails failed: {stats['failed']}")
        self.logger.info("="*70)

    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        stats = self.email_processor.get_stats()

        return {
            'running': self.running,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'check_count': self.check_count,
            'emails_processed': stats['processed'],
            'emails_saved': stats['saved'],
            'emails_failed': stats['failed']
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for Gmail watcher service."""
    import signal

    # Create service
    config = GmailWatcherConfig()
    service = GmailWatcherService(config)

    # Setup signal handlers
    def signal_handler(sig, frame):
        print("\n")
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start service
    try:
        service.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
