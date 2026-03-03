# Facebook Integration for AI Employee

This folder contains the Facebook integration for the autonomous AI employee system.

## Components

### 1. Folder Structure
- `Draft/` - Content that needs to be reviewed and approved
- `Approved/` - Content that has been approved and is ready for posting
- `Need_Action/` - Content that needs modifications
- `Done/` - Posts that have been successfully published
- `logs/` - Log files for the posting process

### 2. Key Files
- `facebook_watcher.py` - Monitors content folders and automatically posts to Facebook
- `facebook_poster.py` - Direct posting script for manual posts
- `skills/facebook_skill.py` - AI skill for Facebook integration
- `skills/instagram_skill.py` - AI skill for Instagram integration (through Facebook)

## Setup

### Facebook App Configuration
1. Create a Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Create a Facebook Page for your business
3. Get the required credentials:
   - App ID
   - App Secret
   - Page ID
   - Long-lived Access Token

### Environment Variables
Add the following to your `.env` file:
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_TOKEN=your_long_lived_access_token
FACEBOOK_PAGE_ID=your_page_id

# Twitter/X API credentials (optional)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Token Management
Facebook access tokens expire after a certain period. To get a new long-lived token:
1. Go to the [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Get a short-lived token (valid for 1-2 hours)
4. Exchange it for a long-lived token (valid for about 60 days) using the token helper:

```bash
python facebook/facebook_token_helper.py
```

### Token Renewal
If you get "Session has expired" errors, you need to renew your token using the Facebook Graph API Explorer or by exchanging a short-lived token for a long-lived one.

## Usage

### Automatic Posting
Run the Facebook watcher to automatically post scheduled content:
```bash
python facebook/facebook_watcher.py
```

Run in dry-run mode to test without posting:
```bash
python facebook/facebook_watcher.py --dry-run
```

Run once and exit:
```bash
python facebook/facebook_watcher.py --once
```

### Direct Posting
Post content directly from a file:
```bash
python facebook/facebook_poster.py --file path/to/post_file.md
```

Post direct content:
```bash
python facebook/facebook_poster.py --content "Your post content here"
```

### Using the AI Skills
The Facebook and Instagram skills can be used by the orchestrator:
- `post_message` - Post a message to Facebook or Instagram
- `get_summary` - Get recent posts summary
- `check_credentials` - Verify API credentials

## Content Format
Markdown files should follow this format:
```markdown
# Facebook Post Title

## Content Details
- **Status:** Draft
- **Category:** Your category
- **Topic:** Your topic

## Post Content
Your actual post content goes here...

## Approval Instructions
- [ ] Review content
- [ ] Approve for posting
- [ ] Post to Facebook
```

## File Movement
- Draft files are moved to `Approved/` folder when ready for posting
- Posted files are moved to `Done/` folder with timestamp
- Files with issues are moved to `Need_Action/` folder

## Error Handling
- Failed posts remain in the source folder
- Errors are logged to the `logs/` folder
- The system continues processing other files even if one fails