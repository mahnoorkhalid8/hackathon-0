"""
CLI tool for Instagram Business operations
Provides command-line interface for posting and managing Instagram content
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv("../.env")

from instagram_auth import InstagramAuth, save_credentials_to_env
from social_media_server import post_instagram_image, get_instagram_insights


def cmd_auth(args):
    """Handle authentication flow"""
    print("Instagram Business Authentication")
    print("=" * 50)

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    redirect_uri = args.redirect_uri or os.getenv("FACEBOOK_REDIRECT_URI", "https://localhost/")

    if not app_id or not app_secret:
        print("Error: FACEBOOK_APP_ID and FACEBOOK_APP_SECRET must be set in .env")
        return 1

    if not args.code:
        # Show authorization URL
        auth_url = (
            f"https://www.facebook.com/v21.0/dialog/oauth?"
            f"client_id={app_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"
        )
        print("\nStep 1: Visit this URL to authorize:")
        print(auth_url)
        print("\nStep 2: After authorization, run:")
        print(f"  python cli.py auth --code YOUR_AUTH_CODE")
        return 0

    # Complete auth flow
    print("\nExchanging authorization code for tokens...")
    auth = InstagramAuth(app_id, app_secret, redirect_uri)

    try:
        result = auth.complete_auth_flow(args.code)

        if result["success"]:
            print("\n✅ Authentication successful!")
            print(json.dumps(result["credentials"], indent=2))

            # Save to .env
            if save_credentials_to_env(result["credentials"], "../.env"):
                print("\n✅ Credentials saved to .env file")
            else:
                print("\n⚠️  Warning: Failed to save credentials to .env")

            return 0
        else:
            print(f"\n❌ Authentication failed: {result.get('error')}")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_post(args):
    """Post an image to Instagram"""
    print("Posting to Instagram")
    print("=" * 50)

    if not args.image_url:
        print("Error: --image-url is required")
        return 1

    print(f"\nImage URL: {args.image_url}")
    print(f"Caption: {args.caption or '(none)'}")
    print(f"Location: {args.location or '(none)'}")

    if not args.yes:
        confirm = input("\nProceed with posting? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return 0

    print("\nCreating media container...")
    result = post_instagram_image(
        image_url=args.image_url,
        caption=args.caption,
        location_id=args.location
    )

    if result["success"]:
        print(f"\n✅ Posted successfully!")
        print(f"Post ID: {result['post_id']}")
        print(f"\nView on Instagram: https://www.instagram.com/p/{result['post_id']}/")
        return 0
    else:
        print(f"\n❌ Posting failed: {result['error']}")
        if "details" in result:
            print(json.dumps(result["details"], indent=2))
        return 1


def cmd_insights(args):
    """Get insights for a post"""
    print("Instagram Post Insights")
    print("=" * 50)

    if not args.media_id:
        print("Error: --media-id is required")
        return 1

    metrics = args.metrics.split(",") if args.metrics else None

    print(f"\nMedia ID: {args.media_id}")
    print(f"Metrics: {metrics or 'default (engagement, impressions, reach, saved)'}")

    result = get_instagram_insights(args.media_id, metrics)

    if result["success"]:
        print("\n✅ Insights retrieved:")
        for insight in result["insights"]:
            name = insight["name"]
            value = insight["values"][0]["value"]
            print(f"  {name}: {value}")
        return 0
    else:
        print(f"\n❌ Failed to get insights: {result['error']}")
        return 1


def cmd_refresh(args):
    """Refresh access token"""
    print("Refreshing Access Token")
    print("=" * 50)

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    current_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not app_id or not app_secret or not current_token:
        print("Error: Missing credentials in .env file")
        return 1

    auth = InstagramAuth(app_id, app_secret, "https://localhost/")

    try:
        print("\nRefreshing token...")
        result = auth.refresh_long_lived_token(current_token)

        if result["success"]:
            print("\n✅ Token refreshed successfully!")
            print(f"Expires at: {result['expires_at']}")

            # Save to .env
            credentials = {
                "INSTAGRAM_ACCESS_TOKEN": result["access_token"],
                "IG_TOKEN_EXPIRES_AT": result["expires_at"]
            }

            if save_credentials_to_env(credentials, "../.env"):
                print("✅ New token saved to .env file")
            else:
                print("⚠️  Warning: Failed to save token to .env")

            return 0
        else:
            print(f"\n❌ Token refresh failed: {result.get('error')}")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_status(args):
    """Check authentication status"""
    print("Instagram Authentication Status")
    print("=" * 50)

    business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    expires_at = os.getenv("IG_TOKEN_EXPIRES_AT")

    print(f"\nBusiness ID: {business_id or '(not set)'}")
    print(f"Access Token: {'✅ Set' if access_token else '❌ Not set'}")
    print(f"Expires At: {expires_at or '(not set)'}")

    if expires_at:
        is_expired = InstagramAuth.is_token_expired(expires_at)
        if is_expired:
            print("\n⚠️  Token is expired or will expire soon")
            print("Run: python cli.py refresh")
        else:
            print("\n✅ Token is valid")

    if not business_id or not access_token:
        print("\n❌ Not authenticated")
        print("Run: python cli.py auth")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Business CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Instagram")
    auth_parser.add_argument("--code", help="Authorization code from OAuth callback")
    auth_parser.add_argument("--redirect-uri", help="OAuth redirect URI")

    # Post command
    post_parser = subparsers.add_parser("post", help="Post an image to Instagram")
    post_parser.add_argument("--image-url", required=True, help="Public URL of the image")
    post_parser.add_argument("--caption", help="Post caption")
    post_parser.add_argument("--location", help="Instagram location ID")
    post_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    # Insights command
    insights_parser = subparsers.add_parser("insights", help="Get post insights")
    insights_parser.add_argument("--media-id", required=True, help="Instagram media ID")
    insights_parser.add_argument("--metrics", help="Comma-separated metrics (engagement,impressions,reach,saved)")

    # Refresh command
    subparsers.add_parser("refresh", help="Refresh access token")

    # Status command
    subparsers.add_parser("status", help="Check authentication status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handlers
    commands = {
        "auth": cmd_auth,
        "post": cmd_post,
        "insights": cmd_insights,
        "refresh": cmd_refresh,
        "status": cmd_status
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
