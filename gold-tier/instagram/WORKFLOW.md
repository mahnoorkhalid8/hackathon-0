# Instagram Workflow Manager

Automated Instagram posting with folder-based workflow management.

## Workflow Overview

```
Drafts/     → Where you create initial posts (images + captions)
    ↓
Approved/   → Move here when ready to post (triggers auto-posting)
    ↓
Public/     → Images copied here and served via HTTP (Instagram needs public URLs)
    ↓
Done/       → Successfully posted content (archived with timestamp)
    ↓
Failed/     → Failed posts (with error logs for debugging)
```

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Folder Structure

```bash
python ig_workflow_manager.py --setup
```

This creates:
- `workflow/Drafts/` - Your working folder
- `workflow/Approved/` - Ready to post
- `workflow/Public/` - Served via HTTP
- `workflow/Done/` - Successfully posted
- `workflow/Failed/` - Failed posts

### 3. Start Public Image Server

**Option A: Local Server (for testing)**
```bash
python public_server.py
```
Server runs at: `http://localhost:8000`

**Option B: Public Server (for production)**
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```
You'll get a public URL like: `https://abc123.ngrok.io`

Update `workflow_config.json`:
```json
{
  "public_url_base": "https://abc123.ngrok.io"
}
```

### 4. Start Workflow Manager

```bash
python ig_workflow_manager.py
```

Now monitoring `workflow/Approved/` for new images!

## Usage

### Basic Workflow

1. **Create a post in Drafts/**
   ```
   workflow/Drafts/
   ├── sunset.jpg          (your image)
   └── sunset.txt          (your caption)
   ```

2. **Write your caption** (`sunset.txt`):
   ```
   Beautiful sunset at the beach 🌅

   #sunset #beach #nature #photography #instagram
   ```

3. **Move to Approved/** when ready:
   ```bash
   mv workflow/Drafts/sunset.* workflow/Approved/
   ```

4. **Automatic posting happens!**
   - Image copied to Public/
   - Posted to Instagram
   - Moved to Done/ with timestamp

### Manual Posting

Post a specific image without monitoring:

```bash
python ig_workflow_manager.py --manual sunset.jpg
```

### Scan Existing Files

Process all images in Approved/ folder once:

```bash
python ig_workflow_manager.py --scan-only
```

### Dry Run (Test Mode)

Test without actually posting:

```bash
python ig_workflow_manager.py --dry-run
```

## Configuration

Edit `workflow_config.json`:

```json
{
  "drafts_folder": "workflow/Drafts",
  "approved_folder": "workflow/Approved",
  "public_folder": "workflow/Public",
  "done_folder": "workflow/Done",
  "failed_folder": "workflow/Failed",
  "public_url_base": "http://localhost:8000",
  "supported_image_formats": [".jpg", ".jpeg", ".png"],
  "caption_format": ".txt",
  "auto_post": true,
  "dry_run": false
}
```

### Configuration Options

- **public_url_base**: Base URL for public image access (update for ngrok)
- **auto_post**: Automatically post when files appear in Approved/
- **dry_run**: Simulate posting without actually posting
- **supported_image_formats**: Image file extensions to process

## File Naming Convention

For an image named `sunset.jpg`:
- Image: `sunset.jpg`
- Caption: `sunset.txt` (optional)

The caption file must have the same name as the image (different extension).

## Monitoring Output

```
============================================================
Processing: sunset.jpg
============================================================
  Caption: Beautiful sunset at the beach 🌅...
  Copying to Public folder...
  Public URL: http://localhost:8000/sunset.jpg
  Posting to Instagram...
  ✓ Posted successfully!
  Post ID: 18123456789012345
  ✓ Moved to Done: workflow/Done/20260305_154530
```

## Logs

All operations are logged to `logs/workflow_logs.json`:

```json
{
  "timestamp": "2026-03-05T15:45:30Z",
  "tool": "workflow_post_success",
  "input": {
    "image": "workflow/Approved/sunset.jpg",
    "caption": "Beautiful sunset...",
    "public_url": "http://localhost:8000/sunset.jpg"
  },
  "response": {
    "post_id": "18123456789012345"
  },
  "status": "success"
}
```

## Folder Structure After Processing

```
workflow/
├── Drafts/              (empty - files moved to Approved)
├── Approved/            (empty - files moved to Done)
├── Public/
│   └── sunset.jpg       (served via HTTP)
└── Done/
    └── 20260305_154530/
        ├── sunset.jpg
        └── sunset.txt
```

## Error Handling

If posting fails, files are moved to `Failed/` with error log:

```
workflow/Failed/20260305_154530/
├── sunset.jpg
├── sunset.txt
└── error.txt           (contains error details)
```

## Advanced Usage

### Batch Processing

Place multiple images in Approved/:

```bash
cp workflow/Drafts/*.jpg workflow/Approved/
```

Each will be processed automatically.

### Disable Auto-Posting

Edit `workflow_config.json`:
```json
{
  "auto_post": false
}
```

Then manually trigger:
```bash
python ig_workflow_manager.py --manual image.jpg
```

### Custom Folders

Edit `workflow_config.json` to use different folder names:
```json
{
  "drafts_folder": "my_drafts",
  "approved_folder": "ready_to_post"
}
```

## Troubleshooting

### "Image could not be downloaded"

**Problem**: Instagram can't access your image URL

**Solutions**:
1. Check public server is running: `python public_server.py`
2. Verify URL is accessible: Open `http://localhost:8000/image.jpg` in browser
3. For production, use ngrok: `ngrok http 8000`
4. Update `public_url_base` in config with ngrok URL

### Files not being processed

**Problem**: Workflow manager not detecting new files

**Solutions**:
1. Check monitoring is running: `python ig_workflow_manager.py`
2. Verify files are in correct folder: `workflow/Approved/`
3. Check file extension is supported: `.jpg`, `.jpeg`, `.png`
4. Try manual trigger: `python ig_workflow_manager.py --manual image.jpg`

### Caption not included

**Problem**: Post has no caption

**Solutions**:
1. Create caption file with same name: `image.txt` for `image.jpg`
2. Verify caption file is in same folder as image
3. Check caption file encoding is UTF-8

## Integration with Autonomous Employee

The workflow manager can be integrated into your autonomous employee system:

1. **Email trigger**: Email handler moves attachments to Drafts/
2. **AI caption generation**: Agent writes captions to .txt files
3. **Approval system**: Human or AI moves to Approved/
4. **Automatic posting**: Workflow manager handles the rest

## Command Reference

```bash
# Setup
python ig_workflow_manager.py --setup

# Start monitoring
python ig_workflow_manager.py

# Manual post
python ig_workflow_manager.py --manual image.jpg

# Scan once
python ig_workflow_manager.py --scan-only

# Dry run
python ig_workflow_manager.py --dry-run

# Start public server
python public_server.py
python public_server.py --port 8080

# With ngrok
ngrok http 8000
```

## Next Steps

1. Test with a sample image
2. Set up ngrok for public access
3. Integrate with your autonomous employee
4. Add scheduled posting (cron job)
5. Add caption AI generation

## Support

- Main docs: `README.md`
- Test suite: `test_instagram.py`
- Examples: `examples.py`
