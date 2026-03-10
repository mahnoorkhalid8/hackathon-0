# Twitter/X Integration for AI Employee Vault

This project includes a comprehensive Twitter/X posting system that integrates with the AI Employee Vault workflow.

## Components

### 1. Twitter Personal Poster (`twitter_personal_poster.py`)
- Uses Playwright browser automation to post to personal Twitter/X profile
- No API key required (uses browser automation instead of paid Twitter API)
- Session persistence - logs in once, stays logged in automatically
- Processes approved Twitter posts from the `Approved` folder

### 2. Twitter Draft Creator (`create_twitter_draft.py`)
- Creates Twitter/X post drafts in the `Need_Action` folder
- Validates character count (max 280 characters)
- Generates unique IDs for each post
- Includes appropriate metadata

## Usage Workflow

### Creating Twitter Posts
1. Create a draft: `python create_twitter_draft.py "Your tweet content"`
2. Or use special content types:
   - `python create_twitter_draft.py --gold-tier` - For Gold Tier features
   - `python create_twitter_draft.py --twitter-integration` - For Twitter features
   - `python create_twitter_draft.py --odoo-integration` - For Odoo integration
   - `python create_twitter_draft.py --audit-summary` - For audit features
   - `python create_twitter_draft.py --all` - All content types

### Processing Twitter Posts
1. Review and edit the draft in `Need_Action/X_POST_*.md`
2. Move to `Approved` folder when ready
3. Run: `python twitter_personal_poster.py`
4. The system will automatically post to your Twitter/X profile
5. After posting, the file moves to `Done` folder

## Features

### Gold Tier Features (as per requirements)
- **Cross-Domain Integration**: Full integration with Facebook, Instagram, and Twitter/X
- **Browser Automation**: No paid API required - uses Playwright to automate Twitter
- **Session Persistence**: Secure session storage with cookies and localStorage
- **Comprehensive Audit Logging**: Updates Dashboard.md with posting activity
- **Error Recovery**: Graceful handling of various error scenarios
- **Character Count Validation**: Ensures tweets are within Twitter's 280 character limit
- **Manual Fallback**: Provides manual instructions if automation fails

### File Structure
- `Need_Action/X_POST_*.md` - Pending Twitter posts to be approved
- `Approved/X_POST_*.md` - Approved Twitter posts ready to be posted
- `Done/X_POST_*.md` - Successfully posted content
- `twitter_session.json` - Saved browser session state (login credentials safe)

## Security & Privacy
- No Twitter credentials stored in code or .env
- Session state saved locally in JSON format
- Manual login process - you control your credentials
- Browser runs in visible mode for transparency

## Best Practices
- Review all content before moving to Approved folder
- Check character count (max 280 for Twitter)
- Test posting with first manual login
- Keep the `twitter_session.json` file secure