"""
Gmail API Email Service
Sends emails using Gmail API with OAuth2 authentication
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Gmail API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    raise


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailAPIService:
    """Gmail API service for sending emails"""

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        """
        Initialize Gmail API service

        Args:
            credentials_path: Path to OAuth2 credentials file from Google Cloud Console
            token_path: Path to token file (generated after first authentication)
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_path),
                SCOPES
            )

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh the token
                print("Refreshing expired token...")
                creds.refresh(Request())
            else:
                # Run OAuth flow to get new credentials
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        f"Download credentials.json from Google Cloud Console:\n"
                        f"1. Go to https://console.cloud.google.com/\n"
                        f"2. APIs & Services > Credentials\n"
                        f"3. Create OAuth 2.0 Client ID (Desktop app)\n"
                        f"4. Download and save as credentials.json"
                    )

                print(f"No valid token found. Starting OAuth flow...")
                print(f"A browser window will open for authentication.")
                print(f"Sign in with your Gmail account and grant permissions.")

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

                # Save the credentials for future use
                print(f"Saving token to: {self.token_path}")
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                print(f"Token saved successfully!")

        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using Gmail API

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (optional, uses authenticated account)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Dict with success status and message details
        """
        try:
            # Create message
            message = MIMEMultipart()
            message['To'] = to
            message['Subject'] = subject

            if from_email:
                message['From'] = from_email
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc

            # Attach body
            message.attach(MIMEText(body, 'plain'))

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            send_message = {'raw': raw_message}
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            return {
                "success": True,
                "message_id": result.get('id'),
                "to": to,
                "subject": subject,
                "thread_id": result.get('threadId')
            }

        except HttpError as error:
            return {
                "success": False,
                "error": f"Gmail API error: {error}",
                "error_code": error.resp.status if hasattr(error, 'resp') else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_html_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send HTML email using Gmail API

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: Email body (HTML)
            plain_body: Plain text alternative (optional)
            from_email: Sender email (optional)

        Returns:
            Dict with success status and message details
        """
        try:
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['Subject'] = subject

            if from_email:
                message['From'] = from_email

            # Attach plain text version (if provided)
            if plain_body:
                message.attach(MIMEText(plain_body, 'plain'))

            # Attach HTML version
            message.attach(MIMEText(html_body, 'html'))

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            return {
                "success": True,
                "message_id": result.get('id'),
                "to": to,
                "subject": subject
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Convenience function for quick email sending
def send_gmail(to: str, subject: str, body: str, credentials_path: str = "credentials.json") -> Dict[str, Any]:
    """
    Quick function to send email via Gmail API

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        credentials_path: Path to credentials file

    Returns:
        Dict with success status
    """
    gmail = GmailAPIService(credentials_path=credentials_path)
    return gmail.send_email(to, subject, body)
