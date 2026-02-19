"""
LinkedIn OAuth Helper

This script helps you get a LinkedIn access token with the correct permissions.

Usage:
    python linkedin_oauth_helper.py
"""

import os
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key


# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/callback')

# OAuth scopes needed
# NOTE: w_organization_social requires Marketing Developer Platform access
# If you don't have that product enabled, use simplified scopes below
SCOPES = [
    'r_liteprofile',    # Read profile
    'w_member_social'   # Post as yourself
]

# Full scopes (requires Marketing Developer Platform approval):
# SCOPES = [
#     'r_liteprofile',        # Read profile
#     'w_member_social',      # Post as yourself
#     'r_organization_social', # Read organization info
#     'w_organization_social'  # Post to company pages
# ]


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from LinkedIn."""

    authorization_code = None

    def do_GET(self):
        """Handle GET request from LinkedIn OAuth callback."""
        # Parse the authorization code from URL
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <html>
            <head><title>LinkedIn OAuth Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #0077B5;">✓ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <p style="color: #666;">The access token has been saved to your .env file.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            error = params.get('error', ['Unknown error'])[0]
            error_description = params.get('error_description', [''])[0]

            html = f"""
            <html>
            <head><title>LinkedIn OAuth Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #d32f2f;">✗ Authorization Failed</h1>
                <p><strong>Error:</strong> {error}</p>
                <p>{error_description}</p>
                <p>Please try again or check your LinkedIn app settings.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress server log messages."""
        pass


def get_authorization_url():
    """Generate LinkedIn authorization URL."""
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }

    base_url = 'https://www.linkedin.com/oauth/v2/authorization'
    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token."""
    url = 'https://www.linkedin.com/oauth/v2/accessToken'

    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Failed to get access token: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def save_token_to_env(access_token):
    """Save access token to .env file."""
    try:
        set_key(env_path, 'LINKEDIN_ACCESS_TOKEN', access_token)
        print(f"[SUCCESS] Access token saved to .env file")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save token: {e}")
        return False


def main():
    print("="*70)
    print("LinkedIn OAuth Helper")
    print("="*70)
    print()

    # Check if credentials are set
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[ERROR] LinkedIn credentials not found in .env file")
        print()
        print("Please add these to your .env file:")
        print("  LINKEDIN_CLIENT_ID=your_client_id")
        print("  LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("  LINKEDIN_REDIRECT_URI=http://localhost:8000/callback")
        print()
        print("Get credentials from: https://www.linkedin.com/developers/apps")
        return

    print("[INFO] LinkedIn OAuth Configuration")
    print(f"  Client ID: {CLIENT_ID}")
    print(f"  Redirect URI: {REDIRECT_URI}")
    print(f"  Scopes: {', '.join(SCOPES)}")
    print()

    print("[INFO] Required LinkedIn Products:")
    print("  - Sign In with LinkedIn (for r_liteprofile)")
    print("  - Share on LinkedIn (for w_member_social)")
    print("  - Marketing Developer Platform (for w_organization_social)")
    print()
    print("[WARNING] Make sure you have access to these products in LinkedIn Developer Portal")
    print("          Visit: https://www.linkedin.com/developers/apps")
    print()

    input("Press Enter to start OAuth flow...")
    print()

    # Generate authorization URL
    auth_url = get_authorization_url()

    print("[INFO] Opening browser for LinkedIn authorization...")
    print()
    print("If browser doesn't open, visit this URL:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("[INFO] Starting local server on http://localhost:8000")
    print("[INFO] Waiting for LinkedIn authorization...")
    print()

    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)

    # Handle one request (the OAuth callback)
    server.handle_request()

    # Get authorization code
    auth_code = OAuthCallbackHandler.authorization_code

    if not auth_code:
        print("[ERROR] Failed to get authorization code")
        print("[INFO] Please try again or check your LinkedIn app settings")
        return

    print("[SUCCESS] Authorization code received!")
    print()

    # Exchange code for access token
    print("[INFO] Exchanging authorization code for access token...")
    token_response = exchange_code_for_token(auth_code)

    if not token_response:
        print("[ERROR] Failed to get access token")
        return

    access_token = token_response.get('access_token')
    expires_in = token_response.get('expires_in', 0)

    if not access_token:
        print("[ERROR] No access token in response")
        return

    print("[SUCCESS] Access token received!")
    print(f"[INFO] Token expires in: {expires_in} seconds ({expires_in // 86400} days)")
    print()

    # Save to .env file
    print("[INFO] Saving access token to .env file...")
    if save_token_to_env(access_token):
        print()
        print("="*70)
        print("[SUCCESS] Setup Complete!")
        print("="*70)
        print()
        print("Your LinkedIn access token has been saved to .env file.")
        print()
        print("Next steps:")
        print("  1. Test connection: python linkedin_poster.py --test")
        print("  2. List posts: python linkedin_poster.py --list")
        print("  3. Post to LinkedIn: python linkedin_poster.py --post-id 1")
        print("  4. Start watcher: python linkedin_watcher.py")
        print()
        print(f"[NOTE] Token expires in {expires_in // 86400} days. You'll need to refresh it.")
    else:
        print()
        print("[ERROR] Failed to save token to .env file")
        print()
        print("Manual steps:")
        print("  1. Open .env file")
        print("  2. Update LINKEDIN_ACCESS_TOKEN with:")
        print(f"     {access_token}")


if __name__ == "__main__":
    main()
