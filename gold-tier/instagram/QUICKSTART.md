# Instagram Business API - Quick Start Guide

## Installation

```bash
cd instagram
pip install -r requirements.txt
```

## Setup (5 minutes)

### 1. Check Current Status

```bash
python cli.py status
```

### 2. If Not Authenticated

Your credentials are already in the parent `.env` file:
- `INSTAGRAM_BUSINESS_ID`: 984663958071232
- `INSTAGRAM_ACCESS_TOKEN`: Valid until 2026-05-04
- `FACEBOOK_APP_ID`: 910519931351023

### 3. Test the Setup

```bash
python test_instagram.py
```

All tests should pass ✓

## Usage Examples

### Post an Image

```python
from social_media_server import post_instagram_image

result = post_instagram_image(
    image_url="https://picsum.photos/1080/1080",
    caption="Check out this amazing photo! 🌟 #instagram #automation"
)

print(result)
# Output: {"success": true, "post_id": "18123456789012345"}
```

### Get Post Insights

```python
from social_media_server import get_instagram_insights

result = get_instagram_insights(
    media_id="18123456789012345",
    metrics=["engagement", "impressions", "reach", "saved"]
)

print(result)
```

### Using CLI

```bash
# Post an image
python cli.py post --image-url "https://example.com/image.jpg" --caption "My caption"

# Get insights
python cli.py insights --media-id "18123456789012345"

# Refresh token
python cli.py refresh

# Check status
python cli.py status
```

## MCP Server Mode

Run as an MCP server for agent integration:

```bash
python social_media_server.py
```

Available tools:
- `instagram_post_image`
- `instagram_get_insights`

## Audit Logs

All operations are logged to `logs/instagram_logs.json`:

```json
{
  "timestamp": "2026-03-05T12:00:00Z",
  "tool": "instagram_post_image",
  "input": {...},
  "response": {...},
  "status": "success"
}
```

## Token Management

Your token expires: **2026-05-04** (Valid ✓)

To refresh before expiration:

```bash
python cli.py refresh
```

Or programmatically:

```python
from instagram_auth import InstagramAuth

auth = InstagramAuth(app_id, app_secret, redirect_uri)
result = auth.refresh_long_lived_token(current_token)
```

## Image Requirements

- Format: JPG, PNG
- Aspect ratio: 4:5 to 1.91:1
- Min resolution: 320px
- Max file size: 8MB
- Must be publicly accessible via HTTPS

## Troubleshooting

### "Image could not be downloaded"
- Ensure image URL is publicly accessible
- Check image meets Instagram requirements

### "Invalid OAuth access token"
- Run `python cli.py refresh` to get a new token

### "No Instagram Business Account found"
- Ensure Facebook Page is connected to Instagram Business
- Check admin access to the Page

## Next Steps

1. Test posting with a real image
2. Monitor audit logs
3. Set up token refresh automation (runs every 50 days)
4. Integrate with your autonomous employee workflow

## Support

- Full documentation: `README.md`
- Examples: `examples.py`
- Tests: `test_instagram.py`
