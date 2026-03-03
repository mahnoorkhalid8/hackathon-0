# Facebook and Instagram Integration for Gold Tier

## Overview
This document describes the Facebook and Instagram integration components built for the Gold Tier autonomous employee system.

## Components Created

### 1. Facebook Integration (`facebook/` folder)
- **Folder Structure:**
  - `Draft/` - Content that needs to be reviewed and approved
  - `Approved/` - Content that has been approved and is ready for posting
  - `Need_Action/` - Content that needs modifications
  - `Done/` - Posts that have been successfully published
  - `logs/` - Log files for the posting process

- **Key Files:**
  - `facebook_watcher.py` - Monitors content folders and automatically posts to Facebook
  - `facebook_poster.py` - Direct posting script for manual posts
  - `facebook_token_helper.py` - Tool to check and manage Facebook tokens

### 2. AI Skills (`skills/` folder)
- `facebook_skill.py` - AI skill for Facebook integration
- `instagram_skill.py` - AI skill for Instagram integration (through Facebook Graph API)
- `twitter_skill.py` - AI skill for Twitter/X integration

### 3. Service Integration
- `facebook_watcher_service.py` - Service wrapper for running the Facebook watcher

## Setup Instructions

### Facebook App Configuration
1. Create a Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Create a Facebook Page for your business
3. Configure the app with the following permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`

### Environment Variables
Add to your `.env` file:
```
# Facebook API credentials
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
Facebook access tokens expire. To get a long-lived token:
1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Get a short-lived token
4. Exchange it for a long-lived token (valid for ~60 days)

Use the token helper to verify your token:
```bash
python facebook/facebook_token_helper.py
```

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
The skills can be used by the orchestrator system:

**Facebook Skill:**
- `post_message` - Post a message to Facebook
- `get_summary` - Get recent posts summary
- `check_credentials` - Verify API credentials

**Instagram Skill:**
- `post_message` - Post a message to Instagram
- `get_summary` - Get recent posts summary
- `check_credentials` - Verify API credentials

**Twitter Skill:**
- `post_tweet` - Post a tweet to Twitter/X
- `get_tweets` - Get recent tweets
- `check_credentials` - Verify API credentials

## Content Format
For automatic processing, create markdown files in the `facebook/Draft/` folder with this format:
```markdown
# Facebook Post Draft

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

## File Movement Flow
1. Draft files are placed in `facebook/Draft/`
2. When ready to post, they are moved to `facebook/Approved/` (automatically or manually)
3. After successful posting, they are moved to `facebook/Done/` with timestamp
4. Files with issues are moved to `facebook/Need_Action/`

## Error Handling
- Failed posts remain in the source folder with error messages logged
- The system continues processing other files even if one fails
- All activities are logged to the `facebook/logs/` folder

## Integration with Main System
The Facebook integration follows the same pattern as LinkedIn integration:
- Content flows through Draft → Approved → Done workflow
- Automatic posting when conditions are met
- Error recovery and logging
- Integration with the main orchestrator system

## Testing
Run the test scripts to verify functionality:
- `python test_facebook.py` - Test Facebook API connection
- `python test_twitter_skill.py` - Test Twitter skill
- `python facebook/facebook_watcher.py --once` - Test watcher once

## Troubleshooting
- **Expired tokens**: Use the token helper to verify and refresh tokens
- **Permission errors**: Ensure your Facebook app has the correct permissions
- **API rate limits**: Implement backoff strategies for high-volume posting
- **Missing dependencies**: Install requirements with `pip install -r requirements.txt`