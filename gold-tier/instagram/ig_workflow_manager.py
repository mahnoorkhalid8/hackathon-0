"""
Instagram Workflow Manager
Manages the lifecycle of Instagram posts through folder-based workflow
Monitors Approved/ folder and automatically posts to Instagram
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Watchdog for file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: watchdog library not installed")
    print("Install with: pip install watchdog")
    sys.exit(1)

# Load environment
load_dotenv("../.env")

# Import Instagram posting function and error recovery
from social_media_server import post_instagram_image, AuditLogger
from error_recovery import InstagramErrorRecovery


class WorkflowConfig:
    """Configuration for workflow manager"""

    def __init__(self, config_file: str = "workflow_config.json"):
        self.config_file = Path(config_file)
        self.load_config()

    def load_config(self):
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            config = json.loads(self.config_file.read_text())
        else:
            config = self.get_default_config()
            self.save_config(config)

        self.drafts_folder = Path(config.get("drafts_folder", "workflow/Drafts"))
        self.approved_folder = Path(config.get("approved_folder", "workflow/Approved"))
        self.public_folder = Path(config.get("public_folder", "workflow/Public"))
        self.done_folder = Path(config.get("done_folder", "workflow/Done"))
        self.failed_folder = Path(config.get("failed_folder", "workflow/Failed"))

        self.public_url_base = config.get("public_url_base", "http://localhost:8000")
        self.supported_image_formats = config.get("supported_image_formats", [".jpg", ".jpeg", ".png"])
        self.caption_format = config.get("caption_format", ".md")
        self.auto_post = config.get("auto_post", True)
        self.dry_run = config.get("dry_run", False)

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "drafts_folder": "workflow/Drafts",
            "approved_folder": "workflow/Approved",
            "public_folder": "workflow/Public",
            "done_folder": "workflow/Done",
            "failed_folder": "workflow/Failed",
            "public_url_base": "http://localhost:8000",
            "supported_image_formats": [".jpg", ".jpeg", ".png"],
            "caption_format": ".md",
            "auto_post": True,
            "dry_run": False
        }

    def save_config(self, config: Dict):
        """Save configuration to file"""
        self.config_file.write_text(json.dumps(config, indent=2))

    def create_folders(self):
        """Create all workflow folders if they don't exist"""
        for folder in [
            self.drafts_folder,
            self.approved_folder,
            self.public_folder,
            self.done_folder,
            self.failed_folder
        ]:
            folder.mkdir(parents=True, exist_ok=True)


class InstagramWorkflowManager:
    """Manages Instagram posting workflow"""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.logger = AuditLogger("logs/workflow_logs.json")
        self.error_recovery = InstagramErrorRecovery(self.logger)
        self.processing = set()  # Track files being processed

        # Create folders
        self.config.create_folders()

        print(f"Instagram Workflow Manager initialized")
        print(f"Monitoring: {self.config.approved_folder}")
        print(f"Public URL: {self.config.public_url_base}")
        print(f"Dry run: {self.config.dry_run}")

    def find_caption_file(self, image_path: Path) -> Optional[Path]:
        """
        Find caption file for an image

        Args:
            image_path: Path to image file

        Returns:
            Path to caption file or None
        """
        caption_path = image_path.with_suffix(self.config.caption_format)
        if caption_path.exists():
            return caption_path
        return None

    def read_caption(self, caption_path: Path) -> str:
        """
        Read caption from file

        Args:
            caption_path: Path to caption file

        Returns:
            Caption text
        """
        try:
            return caption_path.read_text(encoding='utf-8').strip()
        except Exception as e:
            self.logger.log(
                "read_caption_error",
                {"caption_path": str(caption_path)},
                {"error": str(e)},
                "error"
            )
            return ""

    def copy_to_public(self, image_path: Path) -> Tuple[Path, str]:
        """
        Copy image to Public folder and generate public URL

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (public_path, public_url)
        """
        public_path = self.config.public_folder / image_path.name
        shutil.copy2(image_path, public_path)

        # Generate public URL
        public_url = f"{self.config.public_url_base}/{image_path.name}"

        return public_path, public_url

    def move_to_done(self, image_path: Path, caption_path: Optional[Path], public_path: Path):
        """
        Move files to Done folder after successful posting

        Args:
            image_path: Original image path
            caption_path: Caption file path (if exists)
            public_path: Public folder image path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        done_subfolder = self.config.done_folder / timestamp
        done_subfolder.mkdir(exist_ok=True)

        # Move original image
        shutil.move(str(image_path), str(done_subfolder / image_path.name))

        # Move caption if exists
        if caption_path and caption_path.exists():
            shutil.move(str(caption_path), str(done_subfolder / caption_path.name))

        # Keep public file for reference (or delete if you prefer)
        # For now, we'll keep it
        print(f"  ✓ Moved to Done: {done_subfolder}")

    def move_to_failed(self, image_path: Path, caption_path: Optional[Path], error: str):
        """
        Move files to Failed folder after posting failure

        Args:
            image_path: Original image path
            caption_path: Caption file path (if exists)
            error: Error message
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failed_subfolder = self.config.failed_folder / timestamp
        failed_subfolder.mkdir(exist_ok=True)

        # Move original image
        if image_path.exists():
            shutil.move(str(image_path), str(failed_subfolder / image_path.name))

        # Move caption if exists
        if caption_path and caption_path.exists():
            shutil.move(str(caption_path), str(failed_subfolder / caption_path.name))

        # Write error log
        error_log = failed_subfolder / "error.txt"
        error_log.write_text(f"Failed at: {datetime.now().isoformat()}\nError: {error}")

        print(f"  ✗ Moved to Failed: {failed_subfolder}")

    def move_back_to_drafts(self, image_path: Path, caption_path: Optional[Path], error_note: str):
        """
        Move files back to Drafts with error note for manual review

        Args:
            image_path: Original image path
            caption_path: Caption file path (if exists)
            error_note: Detailed error note
        """
        # Move image back to Drafts
        if image_path.exists():
            draft_image = self.config.drafts_folder / image_path.name
            shutil.move(str(image_path), str(draft_image))
            print(f"  ↩ Moved image back to Drafts: {draft_image}")

        # Move caption back to Drafts
        if caption_path and caption_path.exists():
            draft_caption = self.config.drafts_folder / caption_path.name
            shutil.move(str(caption_path), str(draft_caption))
            print(f"  ↩ Moved caption back to Drafts: {draft_caption}")

        # Create error note
        error_note_path = self.config.drafts_folder / f"{image_path.stem}.error"
        error_note_path.write_text(error_note, encoding='utf-8')
        print(f"  📝 Created error note: {error_note_path}")
        print(f"\n  ⚠️  Manual review required. Check {error_note_path.name} for details.")

    def process_image(self, image_path: Path):
        """
        Process an image file for posting with "Ralph Wiggum" retry loop
        Implements intelligent error recovery and graceful degradation

        Args:
            image_path: Path to image file
        """
        # Check if already processing
        if str(image_path) in self.processing:
            return

        self.processing.add(str(image_path))

        try:
            print(f"\n{'='*60}")
            print(f"Processing: {image_path.name}")
            print(f"{'='*60}")

            # Find caption file
            caption_path = self.find_caption_file(image_path)
            original_caption = ""
            current_caption = ""

            if caption_path:
                original_caption = self.read_caption(caption_path)
                current_caption = original_caption
                print(f"  Caption: {current_caption[:50]}..." if len(current_caption) > 50 else f"  Caption: {current_caption}")
            else:
                print(f"  Caption: (none)")

            # Copy to Public folder and get URL
            print(f"  Copying to Public folder...")
            public_path, public_url = self.copy_to_public(image_path)
            print(f"  Public URL: {public_url}")

            # Verify public file exists
            if not public_path.exists():
                print(f"  ⚠️  Warning: Image not found in Public folder after copy")

            if self.config.dry_run:
                print(f"  [DRY RUN] Would post to Instagram")
                print(f"  [DRY RUN] Would move to Done folder")
                self.logger.log(
                    "dry_run_post",
                    {
                        "image": str(image_path),
                        "caption": current_caption,
                        "public_url": public_url
                    },
                    {"status": "dry_run"},
                    "success"
                )
                return

            # === RALPH WIGGUM RETRY LOOP ===
            retry_count = 0
            max_retries = self.error_recovery.MAX_RETRIES
            last_error_analysis = None

            while retry_count <= max_retries:
                attempt_num = retry_count + 1
                print(f"\n  Attempt {attempt_num}/{max_retries + 1}: Posting to Instagram...")

                # Post to Instagram
                result = post_instagram_image(
                    image_url=public_url,
                    caption=current_caption
                )

                # === SUCCESS PATH ===
                if result.get("success"):
                    post_id = result.get("post_id")
                    print(f"  ✓ Posted successfully!")
                    print(f"  Post ID: {post_id}")

                    if retry_count > 0:
                        print(f"  ℹ️  Success after {retry_count} retry(ies)")

                    # Move to Done
                    self.move_to_done(image_path, caption_path, public_path)

                    self.logger.log(
                        "workflow_post_success",
                        {
                            "image": str(image_path),
                            "caption": current_caption,
                            "public_url": public_url,
                            "retry_count": retry_count
                        },
                        {"post_id": post_id},
                        "success"
                    )
                    return  # Success! Exit the retry loop

                # === FAILURE PATH - ANALYZE ERROR ===
                print(f"  ✗ Posting failed")

                # Analyze the error
                error_analysis = self.error_recovery.analyze_error(result)
                last_error_analysis = error_analysis

                print(f"  Error Type: {error_analysis['error_type']}")
                print(f"  Error Code: {error_analysis['error_code']}")
                print(f"  Error Message: {error_analysis['error_message']}")
                print(f"  Recovery Action: {error_analysis['recovery_action']}")

                # Log the error
                self.logger.log(
                    "workflow_post_error",
                    {
                        "image": str(image_path),
                        "caption": current_caption,
                        "public_url": public_url,
                        "attempt": attempt_num
                    },
                    error_analysis,
                    "error"
                )

                # === RECOVERY ACTIONS ===
                if error_analysis['recovery_action'] == 'check_token_expiration':
                    # Check token expiration
                    expires_at = os.getenv("IG_TOKEN_EXPIRES_AT")
                    if expires_at:
                        is_expired, message = self.error_recovery.check_token_expiration(expires_at)
                        print(f"  Token Status: {message}")

                        if is_expired:
                            # Log critical error for CEO briefing
                            self.error_recovery.log_critical_error(
                                "instagram_token_expired",
                                f"Instagram access token expired at {expires_at}. Manual refresh required.",
                                {
                                    "image": str(image_path),
                                    "expires_at": expires_at,
                                    "action_required": "Run: python cli.py refresh"
                                }
                            )
                            print(f"  🚨 CRITICAL: Token expired - logged for CEO briefing")
                    break  # Can't recover from expired token

                elif error_analysis['recovery_action'] == 'truncate_caption':
                    # Truncate caption and retry
                    if retry_count < max_retries:
                        print(f"  🔧 Recovery: Truncating caption...")
                        current_caption = self.error_recovery.truncate_caption(current_caption)
                        print(f"  New caption length: {len(current_caption)} chars")
                        retry_count += 1
                        continue  # Retry with truncated caption

                elif error_analysis['recovery_action'] == 'check_public_folder':
                    # Verify public file and URL
                    print(f"  🔧 Recovery: Checking public folder...")
                    if not public_path.exists():
                        print(f"  ✗ Image not found in Public folder: {public_path}")
                        print(f"  Attempting to re-copy...")
                        try:
                            public_path, public_url = self.copy_to_public(image_path)
                            print(f"  ✓ Re-copied to Public folder")
                            if retry_count < max_retries:
                                retry_count += 1
                                continue  # Retry with re-copied image
                        except Exception as e:
                            print(f"  ✗ Re-copy failed: {e}")
                    else:
                        print(f"  ✓ Image exists in Public folder")
                        print(f"  ⚠️  URL may not be accessible: {public_url}")
                        print(f"  Check that public server is running")

                elif error_analysis['recovery_action'] == 'check_public_url':
                    # URL accessibility issue
                    print(f"  🔧 Recovery: Checking public URL accessibility...")
                    print(f"  URL: {public_url}")
                    print(f"  ⚠️  Ensure public server is running: python public_server.py")
                    print(f"  ⚠️  Or update public_url_base in workflow_config.json")

                # Check if we should retry
                if self.error_recovery.should_retry(error_analysis, retry_count):
                    retry_count += 1
                    if retry_count <= max_retries:
                        print(f"  ⟳ Retrying... ({retry_count}/{max_retries})")
                        time.sleep(2)  # Brief delay before retry
                        continue
                else:
                    print(f"  ✗ Error is not recoverable")
                    break

                # If we've exhausted retries
                if retry_count >= max_retries:
                    break

            # === GRACEFUL DEGRADATION ===
            # If we get here, all retries failed
            print(f"\n  ✗ All retry attempts exhausted ({max_retries + 1} attempts)")
            print(f"  ↩ Moving back to Drafts for manual review...")

            # Create detailed error note
            error_note = self.error_recovery.create_error_note(
                last_error_analysis,
                retry_count,
                original_caption if current_caption != original_caption else None
            )

            # Move back to Drafts with error note
            self.move_back_to_drafts(image_path, caption_path, error_note)

            # Log final failure
            self.logger.log(
                "workflow_post_failed_final",
                {
                    "image": str(image_path),
                    "caption": original_caption,
                    "public_url": public_url,
                    "total_attempts": retry_count + 1
                },
                last_error_analysis,
                "error"
            )

        except Exception as e:
            print(f"  ✗ Unexpected error processing image: {e}")

            # Move back to Drafts with error note
            error_note = f"""Instagram Posting Error Report
Generated: {datetime.now().isoformat()}

UNEXPECTED ERROR:
{str(e)}

This was an unexpected system error. Please review the logs and try again.

NEXT STEPS:
1. Check logs/workflow_logs.json for details
2. Verify system configuration
3. Retry posting: python workflow_helper.py approve {image_path.name}
"""
            self.move_back_to_drafts(
                image_path,
                caption_path if 'caption_path' in locals() else None,
                error_note
            )

            self.logger.log(
                "workflow_processing_error",
                {"image": str(image_path)},
                {"error": str(e)},
                "error"
            )

        finally:
            self.processing.discard(str(image_path))

    def scan_approved_folder(self):
        """Scan Approved folder for existing files"""
        print(f"\nScanning {self.config.approved_folder} for existing files...")

        image_files = []
        for ext in self.config.supported_image_formats:
            image_files.extend(self.config.approved_folder.glob(f"*{ext}"))

        if image_files:
            print(f"Found {len(image_files)} image(s) to process")
            for image_path in image_files:
                self.process_image(image_path)
        else:
            print("No images found")

    def manual_post(self, image_name: str):
        """
        Manually trigger posting for a specific image

        Args:
            image_name: Name of image file in Approved folder
        """
        image_path = self.config.approved_folder / image_name

        if not image_path.exists():
            print(f"Error: Image not found: {image_path}")
            return

        if image_path.suffix.lower() not in self.config.supported_image_formats:
            print(f"Error: Unsupported image format: {image_path.suffix}")
            return

        self.process_image(image_path)


class ApprovedFolderHandler(FileSystemEventHandler):
    """Handles file system events in Approved folder"""

    def __init__(self, workflow_manager: InstagramWorkflowManager):
        self.workflow_manager = workflow_manager

    def on_created(self, event):
        """Handle file creation event"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's an image file
        if file_path.suffix.lower() in self.workflow_manager.config.supported_image_formats:
            # Wait a moment to ensure file is fully written
            time.sleep(1)

            if self.workflow_manager.config.auto_post:
                self.workflow_manager.process_image(file_path)
            else:
                print(f"\nNew image detected: {file_path.name}")
                print("Auto-post is disabled. Use manual trigger to post.")


def start_monitoring(config: WorkflowConfig):
    """
    Start monitoring Approved folder

    Args:
        config: Workflow configuration
    """
    workflow_manager = InstagramWorkflowManager(config)

    # Scan for existing files
    workflow_manager.scan_approved_folder()

    # Set up watchdog observer
    event_handler = ApprovedFolderHandler(workflow_manager)
    observer = Observer()
    observer.schedule(event_handler, str(config.approved_folder), recursive=False)
    observer.start()

    print(f"\n{'='*60}")
    print("Monitoring started. Press Ctrl+C to stop.")
    print(f"{'='*60}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        observer.stop()

    observer.join()
    print("Monitoring stopped.")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Instagram Workflow Manager - Automated posting from folders"
    )

    parser.add_argument(
        "--config",
        default="workflow_config.json",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Scan Approved folder once and exit (no monitoring)"
    )

    parser.add_argument(
        "--manual",
        metavar="IMAGE",
        help="Manually post a specific image from Approved folder"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate posting without actually posting"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Create folder structure and configuration file"
    )

    args = parser.parse_args()

    # Load configuration
    config = WorkflowConfig(args.config)

    # Override dry-run if specified
    if args.dry_run:
        config.dry_run = True

    # Setup mode
    if args.setup:
        print("Setting up Instagram Workflow Manager...")
        config.create_folders()
        print(f"\n✓ Folders created:")
        print(f"  - Drafts: {config.drafts_folder}")
        print(f"  - Approved: {config.approved_folder}")
        print(f"  - Public: {config.public_folder}")
        print(f"  - Done: {config.done_folder}")
        print(f"  - Failed: {config.failed_folder}")
        print(f"\n✓ Configuration saved: {config.config_file}")
        print(f"\nNext steps:")
        print(f"1. Start a local web server for Public folder:")
        print(f"   cd {config.public_folder} && python -m http.server 8000")
        print(f"2. Or use ngrok for public access:")
        print(f"   ngrok http 8000")
        print(f"3. Update public_url_base in {config.config_file}")
        print(f"4. Start monitoring:")
        print(f"   python ig_workflow_manager.py")
        return

    # Manual post mode
    if args.manual:
        workflow_manager = InstagramWorkflowManager(config)
        workflow_manager.manual_post(args.manual)
        return

    # Scan only mode
    if args.scan_only:
        workflow_manager = InstagramWorkflowManager(config)
        workflow_manager.scan_approved_folder()
        return

    # Start monitoring
    start_monitoring(config)


if __name__ == "__main__":
    main()
