# Instagram Posting Guide

## Quick Start

### One-Time Setup

1. **Install ngrok** (required for Instagram API):
   - Download: https://ngrok.com/download
   - Extract `ngrok.exe` to any folder
   - No account needed for basic use

2. **Why ngrok?**
   - Instagram API requires a publicly accessible URL to download images
   - Ngrok creates a temporary, secure tunnel (only active while running)
   - Your images are only accessible for a few seconds during posting
   - The tunnel closes when you stop ngrok

### Every Time You Post

**Terminal 1 - Start ngrok:**
```bash
ngrok http 8000
```
Keep this running. You'll see a URL like: `https://abc123.ngrok.io`

**Terminal 2 - Post to Instagram:**
```bash
cd "C:/Users/SEVEN86 COMPUTES/hackthon-0/gold-tier/instagram"

# Move your files to Approved folder
# - Image: post_name.jpg (or .png, .jpeg)
# - Caption: post_name.md

# Run the posting script
python simple_post.py
```

## File Structure

```
workflow/
├── Drafts/          # Prepare your posts here
│   ├── post1.jpg
│   ├── post1.md
│   ├── post2.jpg
│   └── post2.md
├── Approved/        # Move files here when ready to post
├── Public/          # Temporary (auto-managed)
└── Done/            # Successfully posted (auto-archived)
```

## Posting Workflow

1. **Prepare in Drafts:**
   - Create/edit your image: `post_name.jpg`
   - Create/edit your caption: `post_name.md`

2. **Start ngrok** (Terminal 1):
   ```bash
   ngrok http 8000
   ```

3. **Move to Approved** (when ready):
   ```bash
   mv workflow/Drafts/post_name.jpg workflow/Approved/
   mv workflow/Drafts/post_name.md workflow/Approved/
   ```

4. **Post** (Terminal 2):
   ```bash
   python simple_post.py
   ```

5. **Done!**
   - On success: Files move to `Done/TIMESTAMP/`
   - On failure: Files stay in `Approved/` with error details

## Manual Commands

### Post a specific image:
```bash
cd "C:/Users/SEVEN86 COMPUTES/hackthon-0/gold-tier/instagram"
python simple_post.py
```

### Check Instagram connection:
```bash
python get_instagram_id.py
```

### View logs:
```bash
cat logs/workflow_logs.json
```

## Troubleshooting

### "Ngrok is NOT running"
- Start ngrok in a separate terminal: `ngrok http 8000`
- Keep it running while posting

### "No images found in Approved folder"
- Move both image and caption to `workflow/Approved/`
- Files must have matching names (e.g., `post1.jpg` + `post1.md`)

### "Caption file missing"
- Create a `.md` file with the same name as your image
- Example: `post1.jpg` needs `post1.md`

### "Posting failed: Error 9004"
- Ngrok might not be running
- Check ngrok terminal for the public URL

### "Posting failed: Error 100"
- Instagram Business Account not connected
- Run: `python get_instagram_id.py` to verify

## Security Notes

- Ngrok tunnel is temporary (closes when you stop ngrok)
- Images are only accessible during posting (a few seconds)
- No permanent public hosting
- Tunnel URL changes each time you restart ngrok

## Current Status

✅ Instagram Business Account connected
✅ Instagram Business Account ID: 17841456917241432
✅ Access token configured
✅ Caption format: .md files
✅ Supported images: .jpg, .png, .jpeg

## Files Ready to Post

Check your `workflow/Drafts/` folder:
- post1_agentic_ai.jpg + post1_agentic_ai.md
- post2_ai_trends.jpg + post2_ai_trends.md
- post3_project_overview.jpg + post3_project_overview.md
- post4_error_recovery.jpg + post4_error_recovery.md
- post5_ceo_briefing.jpg + post5_ceo_briefing.md
