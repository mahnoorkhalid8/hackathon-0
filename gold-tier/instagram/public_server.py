"""
Simple HTTP server for serving Public folder
Provides public URLs for Instagram image posting
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""

    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def start_server(directory: str = "workflow/Public", port: int = 8000):
    """
    Start HTTP server for Public folder

    Args:
        directory: Directory to serve
        port: Port number
    """
    # Change to the directory
    public_dir = Path(directory)
    if not public_dir.exists():
        print(f"Error: Directory not found: {public_dir}")
        print("Run: python ig_workflow_manager.py --setup")
        sys.exit(1)

    os.chdir(public_dir)

    # Create server
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)

    print(f"=" * 60)
    print(f"Instagram Public Image Server")
    print(f"=" * 60)
    print(f"Serving: {public_dir.absolute()}")
    print(f"URL: http://localhost:{port}")
    print(f"\nTo make this accessible from the internet:")
    print(f"1. Install ngrok: https://ngrok.com/download")
    print(f"2. Run: ngrok http {port}")
    print(f"3. Update public_url_base in workflow_config.json")
    print(f"\nPress Ctrl+C to stop")
    print(f"=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTP server for Instagram Public folder")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--directory", default="workflow/Public", help="Directory to serve")

    args = parser.parse_args()

    start_server(args.directory, args.port)
