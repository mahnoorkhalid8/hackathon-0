"""
Example usage of Instagram Business API integration
Demonstrates authentication, posting, and insights retrieval
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

from instagram_auth import InstagramAuth, save_credentials_to_env
from social_media_server import post_instagram_image, get_instagram_insights


def example_check_token_status():
    """Example: Check if access token is expired"""
    print("=== Checking Token Status ===\n")

    expires_at = os.getenv("IG_TOKEN_EXPIRES_AT")

    if not expires_at:
        print("No token expiration date found in .env")
        return

    is_expired = InstagramAuth.is_token_expired(expires_at)

    if is_expired:
        print(f"⚠️  Token expires at: {expires_at}")
        print("Token is expired or will expire within 7 days")
        print("Run token refresh to get a new token")
    else:
        print(f"✅ Token is valid until: {expires_at}")


def example_refresh_token():
    """Example: Refresh an expiring access token"""
    print("\n=== Refreshing Access Token ===\n")

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    current_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not all([app_id, app_secret, current_token]):
        print("Missing credentials in .env file")
        return

    auth = InstagramAuth(app_id, app_secret, "https://localhost/")

    try:
        result = auth.refresh_long_lived_token(current_token)

        if result["success"]:
            print("✅ Token refreshed successfully!")
            print(f"New expiration: {result['expires_at']}")

            # Save to .env
            credentials = {
                "INSTAGRAM_ACCESS_TOKEN": result["access_token"],
                "IG_TOKEN_EXPIRES_AT": result["expires_at"]
            }
            save_credentials_to_env(credentials, "../.env")
            print("✅ Saved to .env file")
        else:
            print(f"❌ Refresh failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_post_image():
    """Example: Post an image to Instagram"""
    print("\n=== Posting Image to Instagram ===\n")

    # Example image URL (must be publicly accessible)
    image_url = "https://picsum.photos/1080/1080"
    caption = "Beautiful sunset 🌅 #nature #photography #instagram"

    print(f"Image URL: {image_url}")
    print(f"Caption: {caption}\n")

    result = post_instagram_image(
        image_url=image_url,
        caption=caption
    )

    if result["success"]:
        print(f"✅ Posted successfully!")
        print(f"Post ID: {result['post_id']}")
        return result["post_id"]
    else:
        print(f"❌ Posting failed: {result['error']}")
        if "error_code" in result:
            print(f"Error code: {result['error_code']}")
        return None


def example_get_insights(media_id):
    """Example: Get insights for a post"""
    print("\n=== Getting Post Insights ===\n")

    if not media_id:
        print("No media ID provided")
        return

    result = get_instagram_insights(
        media_id=media_id,
        metrics=["engagement", "impressions", "reach", "saved"]
    )

    if result["success"]:
        print("✅ Insights retrieved:\n")
        for insight in result["insights"]:
            name = insight["name"]
            value = insight["values"][0]["value"]
            print(f"  {name}: {value}")
    else:
        print(f"❌ Failed to get insights: {result['error']}")


def example_complete_auth_flow():
    """Example: Complete OAuth authentication flow"""
    print("\n=== Complete Authentication Flow ===\n")

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    redirect_uri = "https://localhost/"

    if not app_id or not app_secret:
        print("Missing Facebook app credentials in .env")
        return

    # Step 1: Show authorization URL
    auth_url = (
        f"https://www.facebook.com/v21.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"
    )

    print("Step 1: Visit this URL to authorize:")
    print(auth_url)
    print("\nStep 2: After authorization, you'll get a code in the redirect URL")
    print("Step 3: Use that code with the auth flow:\n")

    print("Example code:")
    print("  auth = InstagramAuth(app_id, app_secret, redirect_uri)")
    print("  result = auth.complete_auth_flow(authorization_code)")
    print("  save_credentials_to_env(result['credentials'], '../.env')")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Instagram Business API - Usage Examples")
    print("=" * 60)

    # Check token status
    example_check_token_status()

    # Show how to refresh token
    # Uncomment to actually refresh:
    # example_refresh_token()

    # Show how to post (commented out to avoid accidental posting)
    print("\n=== Example: Post Image ===")
    print("To post an image, uncomment the example_post_image() call")
    print("Example code:")
    print('  result = post_instagram_image(')
    print('      image_url="https://example.com/image.jpg",')
    print('      caption="My caption #hashtag"')
    print('  )')

    # Show auth flow
    example_complete_auth_flow()

    print("\n" + "=" * 60)
    print("For more examples, see README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
