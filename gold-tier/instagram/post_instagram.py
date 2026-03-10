"""
Instagram Posting with Temporary Public URL
Uses ngrok to temporarily expose image during posting only
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv

load_dotenv('../.env', override=True)

class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler that doesn't print logs"""
    def log_message(self, format, *args):
        pass

def start_http_server(port=8000):
    """Start HTTP server in background"""
    os.chdir('workflow/Public')
    server = HTTPServer(('', port), QuietHTTPRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    os.chdir('../..')
    return server

def get_ngrok_url():
    """Get ngrok public URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    except:
        return None

def post_to_instagram(image_filename, caption):
    """Post image to Instagram"""
    from social_media_server import post_instagram_image

    # Get ngrok URL
    public_url = get_ngrok_url()
    if not public_url:
        return {"success": False, "error": "Ngrok not running"}

    image_url = f"{public_url}/{image_filename}"
    print(f"Image URL: {image_url}")

    # Post to Instagram
    result = post_instagram_image(image_url, caption)
    return result

def main():
    print("=" * 60)
    print("Instagram Posting with Temporary Public URL")
    print("=" * 60)

    # Check if ngrok is running
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("\n[ERROR] Ngrok is not running!")
        print("\nTo start ngrok:")
        print("1. Download ngrok from: https://ngrok.com/download")
        print("2. Run: ngrok http 8000")
        print("3. Keep ngrok running and run this script again")
        return

    print(f"\n[OK] Ngrok is running: {ngrok_url}")

    # Start HTTP server
    print("[OK] Starting HTTP server on port 8000...")
    server = start_http_server(8000)
    time.sleep(1)

    # Get image and caption from Approved folder
    approved_folder = Path('workflow/Approved')
    images = list(approved_folder.glob('*.jpg')) + list(approved_folder.glob('*.png')) + list(approved_folder.glob('*.jpeg'))

    if not images:
        print("\n[ERROR] No images found in Approved folder")
        print("Move your image and caption to workflow/Approved/ first")
        server.shutdown()
        return

    image_path = images[0]
    caption_path = image_path.with_suffix('.md')

    if not caption_path.exists():
        print(f"\n[ERROR] Caption file not found: {caption_path.name}")
        server.shutdown()
        return

    # Copy image to Public folder
    public_path = Path('workflow/Public') / image_path.name
    import shutil
    shutil.copy2(image_path, public_path)

    # Read caption
    caption = caption_path.read_text(encoding='utf-8').strip()

    print(f"\n[OK] Found image: {image_path.name}")
    print(f"[OK] Found caption: {caption_path.name}")
    print(f"\nPosting to Instagram...")

    # Post to Instagram
    result = post_to_instagram(image_path.name, caption)

    print(f"\nResult: {result}")

    if result.get('success'):
        print("\n[SUCCESS] Posted to Instagram!")

        # Move to Done folder
        done_folder = Path('workflow/Done') / time.strftime('%Y%m%d_%H%M%S')
        done_folder.mkdir(parents=True, exist_ok=True)
        shutil.move(str(image_path), str(done_folder / image_path.name))
        shutil.move(str(caption_path), str(done_folder / caption_path.name))
        print(f"[OK] Moved files to: {done_folder}")
    else:
        print(f"\n[ERROR] Posting failed: {result.get('error')}")

    # Cleanup
    public_path.unlink(missing_ok=True)
    server.shutdown()
    print("\n[OK] HTTP server stopped")
    print("=" * 60)

if __name__ == '__main__':
    main()
