"""
Simple Instagram Posting Script
Just move your files to Approved folder and run this script
"""
import os
import sys
import time
import shutil
import requests
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('../.env', override=True)

class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def check_ngrok():
    """Check if ngrok is running and return public URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    except:
        pass
    return None

def start_local_server():
    """Start local HTTP server"""
    os.chdir('workflow/Public')
    server = HTTPServer(('', 8000), QuietHTTPRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    os.chdir('../..')
    return server

def post_to_instagram(image_url, caption):
    """Post to Instagram using the API"""
    from social_media_server import post_instagram_image
    return post_instagram_image(image_url, caption)

def main():
    print("\n" + "="*60)
    print("Instagram Posting - Simple Workflow")
    print("="*60 + "\n")

    # Step 1: Check ngrok
    print("Step 1: Checking ngrok...")
    ngrok_url = check_ngrok()

    if not ngrok_url:
        print("\n[!] Ngrok is NOT running")
        print("\nYou need ngrok to temporarily expose images to Instagram API.")
        print("\nQuick Setup:")
        print("1. Download: https://ngrok.com/download")
        print("2. Extract ngrok.exe")
        print("3. Open new terminal and run: ngrok http 8000")
        print("4. Keep ngrok running and run this script again\n")
        print("Note: Ngrok creates a temporary URL that expires when you close it.")
        print("Your images are only accessible during posting (a few seconds).\n")
        return

    print(f"[OK] Ngrok running: {ngrok_url}\n")

    # Step 2: Start local server
    print("Step 2: Starting local server...")
    server = start_local_server()
    time.sleep(1)
    print("[OK] Server started on port 8000\n")

    # Step 3: Find files in Approved folder
    print("Step 3: Looking for files in Approved folder...")
    approved = Path('workflow/Approved')

    images = list(approved.glob('*.jpg')) + list(approved.glob('*.png')) + list(approved.glob('*.jpeg'))

    if not images:
        print("[!] No images found in workflow/Approved/")
        print("\nMove your image and caption files to Approved folder:")
        print("  - Image: post_name.jpg (or .png, .jpeg)")
        print("  - Caption: post_name.md\n")
        server.shutdown()
        return

    image_path = images[0]
    caption_path = image_path.with_suffix('.md')

    if not caption_path.exists():
        print(f"[!] Caption file missing: {caption_path.name}")
        print(f"\nCreate a .md file with the same name as your image\n")
        server.shutdown()
        return

    print(f"[OK] Image: {image_path.name}")
    print(f"[OK] Caption: {caption_path.name}\n")

    # Step 4: Copy to Public folder
    print("Step 4: Preparing image...")
    public_path = Path('workflow/Public') / image_path.name
    shutil.copy2(image_path, public_path)
    print(f"[OK] Image ready\n")

    # Step 5: Read caption
    caption = caption_path.read_text(encoding='utf-8').strip()
    print(f"Step 5: Caption loaded ({len(caption)} characters)\n")

    # Step 6: Post to Instagram
    print("Step 6: Posting to Instagram...")
    print("(This may take 10-30 seconds...)\n")

    image_url = f"{ngrok_url}/{image_path.name}"
    result = post_to_instagram(image_url, caption)

    # Step 7: Handle result
    print("\n" + "="*60)
    if result.get('success'):
        print("[SUCCESS] Posted to Instagram!")
        print("="*60 + "\n")

        # Move to Done
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        done_folder = Path('workflow/Done') / timestamp
        done_folder.mkdir(parents=True, exist_ok=True)

        shutil.move(str(image_path), str(done_folder / image_path.name))
        shutil.move(str(caption_path), str(done_folder / caption_path.name))

        print(f"Files moved to: {done_folder}\n")
    else:
        print("[ERROR] Posting failed")
        print("="*60)
        print(f"\nError: {result.get('error')}")
        print(f"Details: {result.get('details', {})}\n")

    # Cleanup
    public_path.unlink(missing_ok=True)
    server.shutdown()
    print("[OK] Cleanup complete\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
