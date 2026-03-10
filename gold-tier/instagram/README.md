# Instagram Business API Integration

Production-ready Python module for Instagram Business automation with OAuth 2.0 authentication and MCP server support.

## Features

- ✅ Complete OAuth 2.0 token exchange flow
- ✅ Long-lived token management (60-day tokens)
- ✅ Automatic token refresh
- ✅ 2-step Instagram posting (Container + Publish)
- ✅ Media insights retrieval
- ✅ Comprehensive audit logging
- ✅ MCP server integration
- ✅ Structured error handling
- ✅ Production-ready code

## Installation

```bash
cd instagram
pip install -r requirements.txt
```

## Environment Setup

Add these variables to your `.env` file (in the parent `gold-tier` directory):

```env
# Facebook App Credentials
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=https://localhost/

# Instagram Business Credentials (obtained after OAuth)
INSTAGRAM_BUSINESS_ID=your_business_id
INSTAGRAM_ACCESS_TOKEN=your_access_token
IG_TOKEN_EXPIRES_AT=2026-05-04
```

## Quick Start

### 1. Authentication (First Time Setup)

```python
from instagram_auth import InstagramAuth, save_credentials_to_env
import os

# Initialize auth manager
auth = InstagramAuth(
    app_id=os.getenv("FACEBOOK_APP_ID"),
    app_secret=os.getenv("FACEBOOK_APP_SECRET"),
    redirect_uri=os.getenv("FACEBOOK_REDIRECT_URI")
)

# Complete OAuth flow with authorization code
result = auth.complete_auth_flow(authorization_code)

# Save credentials to .env
save_credentials_to_env(result["credentials"], "../.env")
```

### 2. Post an Image to Instagram

```python
from social_media_server import post_instagram_image

result = post_instagram_image(
    image_url="https://example.com/image.jpg",
    caption="Check out this amazing photo! #instagram #automation"
)

if result["success"]:
    print(f"Posted! Media ID: {result['post_id']}")
else:
    print(f"Error: {result['error']}")
```

### 3. Get Post Insights

```python
from social_media_server import get_instagram_insights

result = get_instagram_insights(
    media_id="your_media_id",
    metrics=["engagement", "impressions", "reach", "saved"]
)

if result["success"]:
    for insight in result["insights"]:
        print(f"{insight['name']}: {insight['values'][0]['value']}")
```

## MCP Server Usage

Run as an MCP server for agent integration:

```bash
python social_media_server.py
```

Available tools:
- `instagram_post_image` - Post images to Instagram
- `instagram_get_insights` - Get performance metrics

## Authentication Flow

### Step 1: Get Authorization Code

Direct users to:
```
https://www.facebook.com/v21.0/dialog/oauth?
  client_id={app_id}&
  redirect_uri={redirect_uri}&
  scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement
```

### Step 2: Exchange Code for Tokens

```python
auth = InstagramAuth(app_id, app_secret, redirect_uri)
result = auth.complete_auth_flow(authorization_code)
```

This automatically:
1. Exchanges code for short-lived token
2. Exchanges short-lived for long-lived token (60 days)
3. Fetches Page Access Token
4. Gets Instagram Business Account ID

### Step 3: Token Refresh

Check and refresh tokens before they expire:

```python
from instagram_auth import InstagramAuth

auth = InstagramAuth(app_id, app_secret, redirect_uri)

# Check if token needs refresh (7-day buffer)
if auth.is_token_expired(expires_at):
    result = auth.refresh_long_lived_token(current_token)
    save_credentials_to_env({
        "INSTAGRAM_ACCESS_TOKEN": result["access_token"],
        "IG_TOKEN_EXPIRES_AT": result["expires_at"]
    }, "../.env")
```

## API Reference

### InstagramAuth

#### `complete_auth_flow(auth_code: str) -> Dict`
Complete OAuth flow from authorization code to credentials.

**Returns:**
```json
{
  "success": true,
  "credentials": {
    "IG_BUSINESS_ID": "123456789",
    "IG_PAGE_ACCESS_TOKEN": "token...",
    "IG_TOKEN_EXPIRES_AT": "2026-05-04T00:00:00Z",
    "FB_PAGE_ID": "987654321"
  }
}
```

#### `refresh_long_lived_token(current_token: str) -> Dict`
Refresh a long-lived token before expiration.

#### `is_token_expired(expires_at: str, buffer_days: int = 7) -> bool`
Check if token is expired or will expire soon.

### InstagramAPI

#### `post_image(image_url: str, caption: str = None, location_id: str = None) -> Dict`
Post an image to Instagram (2-step process).

**Parameters:**
- `image_url` - Public URL of the image (must be accessible)
- `caption` - Post caption with hashtags
- `location_id` - Instagram location ID (optional)

**Returns:**
```json
{
  "success": true,
  "post_id": "18123456789012345"
}
```

#### `get_media_insights(media_id: str, metrics: list = None) -> Dict`
Get performance insights for a post.

**Metrics:**
- `engagement` - Total interactions
- `impressions` - Total views
- `reach` - Unique accounts reached
- `saved` - Number of saves

## Audit Logging

All API calls are logged to `logs/instagram_logs.json`:

```json
{
  "timestamp": "2026-03-05T12:00:00Z",
  "tool": "instagram_post_image",
  "input": {
    "image_url": "https://example.com/image.jpg",
    "caption": "Test post"
  },
  "response": {
    "status_code": 200,
    "post_id": "18123456789012345"
  },
  "status": "success"
}
```

## Error Handling

All functions return structured error responses:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "token_expired",
  "details": {}
}
```

**Error Types:**
- `token_expired` - Access token has expired
- `invalid_scope` - Missing required permissions
- `permission_denied` - User lacks necessary permissions
- `network_error` - Network request failed

## Image Requirements

For Instagram posting:
- Image must be publicly accessible via HTTPS
- Supported formats: JPG, PNG
- Aspect ratio: 4:5 to 1.91:1
- Min resolution: 320px
- Max file size: 8MB

## Testing

Run the test script:

```bash
python test_instagram.py
```

## Troubleshooting

### "No Instagram Business Account found"
- Ensure your Facebook Page is connected to an Instagram Business account
- Check that you have admin access to the Page

### "Invalid OAuth access token"
- Token may have expired - run refresh flow
- Check that token has required scopes

### "Image could not be downloaded"
- Ensure image URL is publicly accessible
- Check image meets Instagram requirements

## Security Notes

- Never commit `.env` files to version control
- Rotate tokens regularly
- Use HTTPS for all image URLs
- Monitor audit logs for suspicious activity

## License

Part of Gold Tier Autonomous Employee system.
