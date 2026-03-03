# LinkedIn API Setup Guide

**Problem:** Your current access token doesn't have the required permissions to post to LinkedIn.

**Error:** `ACCESS_DENIED - Not enough permissions to access: me.GET.NO_VERSION`

---

## Step 1: Create/Configure LinkedIn App

### 1.1 Go to LinkedIn Developer Portal
- Visit: https://www.linkedin.com/developers/apps
- Sign in with your LinkedIn account

### 1.2 Create New App (or select existing)
- Click "Create app"
- Fill in required information:
  - **App name:** Your app name (e.g., "LinkedIn Auto Poster")
  - **LinkedIn Page:** Select your company page (Outfitterzzz)
  - **App logo:** Upload any logo
  - **Legal agreement:** Check the box
- Click "Create app"

### 1.3 Verify Your App
- LinkedIn will ask you to verify your app
- Follow the verification process
- This may take 1-2 business days

---

## Step 2: Configure OAuth 2.0 Settings

### 2.1 Go to "Auth" Tab
- In your app dashboard, click "Auth" tab

### 2.2 Add Redirect URLs
Add this redirect URL:
```
http://localhost:8000/callback
```

### 2.3 Request API Access (Products Tab)
Go to "Products" tab and request access to:
- **Sign In with LinkedIn** (for r_liteprofile)
- **Share on LinkedIn** (for w_member_social)
- **Marketing Developer Platform** (for w_organization_social - company pages)

**Note:** Some products require approval. Apply and wait for LinkedIn's response.

---

## Step 3: Get OAuth Scopes

You need these scopes for posting:

### For Personal Posts:
- `r_liteprofile` - Read your profile info
- `w_member_social` - Post as yourself

### For Company Page Posts (Outfitterzzz):
- `r_liteprofile` - Read your profile info
- `r_organization_social` - Read organization info
- `w_organization_social` - Post to company pages

---

## Step 4: Generate Access Token

### Method A: Using OAuth 2.0 Flow (Recommended)

I'll create a helper script for you to get the access token:

**Run this script:**
```bash
cd linkedin
python linkedin_oauth_helper.py
```

This will:
1. Open browser for LinkedIn authorization
2. You approve the permissions
3. Script captures the access token
4. Automatically updates your .env file

### Method B: Manual OAuth Flow

1. **Get Authorization Code:**

Visit this URL (replace YOUR_CLIENT_ID):
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback&scope=r_liteprofile%20w_member_social%20w_organization_social
```

2. **Authorize the app** - Click "Allow"

3. **Copy the code** from redirect URL:
```
http://localhost:8000/callback?code=YOUR_AUTHORIZATION_CODE
```

4. **Exchange code for access token:**

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTHORIZATION_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8000/callback"
```

5. **Copy the access_token** from response

---

## Step 5: Update .env File

Open your `.env` file and update:

```env
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
LINKEDIN_ACCESS_TOKEN=your_new_access_token_here
LINKEDIN_API_URL=https://api.linkedin.com/v2/
```

**Important:**
- Access tokens expire (usually 60 days)
- You'll need to refresh them periodically
- Keep your credentials secure

---

## Step 6: Test Connection

```bash
cd linkedin
python linkedin_poster.py --test
```

**Expected output:**
```
[SUCCESS] Connected to LinkedIn API!
[INFO] User ID: XXXXX
[INFO] Name: Your Name
```

---

## Step 7: Start Using the Tools

### Test Posting
```bash
# List your generated posts
python linkedin_poster.py --list

# Post a specific post
python linkedin_poster.py --post-id 1
```

### Start Automatic Watcher
```bash
# Test mode (no actual posting)
python linkedin_watcher.py --dry-run

# Run once
python linkedin_watcher.py --once

# Run continuously (checks every 60 seconds)
python linkedin_watcher.py
```

---

## Troubleshooting

### Error: "ACCESS_DENIED"
**Solution:** Your access token doesn't have required scopes. Regenerate token with correct permissions.

### Error: "INVALID_TOKEN"
**Solution:** Token expired. Generate new access token.

### Error: "Application does not have access to this product"
**Solution:** Request access to required products in LinkedIn Developer Portal.

### Error: "Member does not have permission to create content"
**Solution:** For company pages, make sure you're an admin of the page.

---

## Alternative: Use LinkedIn's Official Partners

If you can't get API access, use these official partners:

### Buffer (Recommended)
- Free plan: 10 scheduled posts
- Official LinkedIn API access
- Easy to use

**Setup:**
1. Sign up: https://buffer.com
2. Connect LinkedIn account
3. Use our tools to generate posts
4. Copy to Buffer for scheduling

### Hootsuite
- More features
- Better for multiple platforms
- Paid plans start at $99/month

---

## Current Status

**Your credentials in .env:**
```
LINKEDIN_CLIENT_ID=77ij4mcj5fjz1b
LINKEDIN_CLIENT_SECRET=LINKEDIN_CLIENT_SECRET
LINKEDIN_ACCESS_TOKEN=AQUvE0_FdtDF0vBlt-8s... (403 error - insufficient permissions)
```

**What you need to do:**
1. Go to LinkedIn Developer Portal
2. Request access to "Share on LinkedIn" product
3. Generate new access token with w_member_social scope
4. Update LINKEDIN_ACCESS_TOKEN in .env
5. Test with: `python linkedin_poster.py --test`

---

## Quick Commands Reference

```bash
# Test API connection
python linkedin_poster.py --test

# List all posts
python linkedin_poster.py --list

# Post specific post by ID
python linkedin_poster.py --post-id 1

# Post all draft posts
python linkedin_poster.py --post-all-drafts

# Start watcher (automatic posting)
python linkedin_watcher.py

# Test watcher without posting
python linkedin_watcher.py --dry-run

# Run watcher once
python linkedin_watcher.py --once
```

---

## Need Help?

If you're stuck:
1. Check LinkedIn Developer Portal for app status
2. Verify you have required product access
3. Make sure access token has correct scopes
4. Consider using Buffer as alternative

The tools are ready - you just need the correct API permissions!
