"""
Test script for Instagram Workflow Manager
Tests folder monitoring, file processing, and lifecycle management
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ig_workflow_manager import WorkflowConfig, InstagramWorkflowManager


def setup_test_environment():
    """Create test environment"""
    print("Setting up test environment...")

    # Create test config
    config = WorkflowConfig("test_workflow_config.json")
    config.drafts_folder = Path("test_workflow/Drafts")
    config.approved_folder = Path("test_workflow/Approved")
    config.public_folder = Path("test_workflow/Public")
    config.done_folder = Path("test_workflow/Done")
    config.failed_folder = Path("test_workflow/Failed")
    config.dry_run = True  # Don't actually post during tests

    config.create_folders()

    print("[PASS] Test folders created")
    return config


def cleanup_test_environment():
    """Clean up test environment"""
    print("\nCleaning up test environment...")
    test_dir = Path("test_workflow")
    if test_dir.exists():
        shutil.rmtree(test_dir)

    config_file = Path("test_workflow_config.json")
    if config_file.exists():
        config_file.unlink()

    print("[PASS] Test environment cleaned")


def test_folder_creation():
    """Test folder structure creation"""
    print("\n=== Test: Folder Creation ===")

    config = WorkflowConfig("test_workflow_config.json")
    config.drafts_folder = Path("test_workflow/Drafts")
    config.approved_folder = Path("test_workflow/Approved")
    config.public_folder = Path("test_workflow/Public")
    config.done_folder = Path("test_workflow/Done")
    config.failed_folder = Path("test_workflow/Failed")

    config.create_folders()

    # Verify all folders exist
    assert config.drafts_folder.exists(), "Drafts folder not created"
    assert config.approved_folder.exists(), "Approved folder not created"
    assert config.public_folder.exists(), "Public folder not created"
    assert config.done_folder.exists(), "Done folder not created"
    assert config.failed_folder.exists(), "Failed folder not created"

    print("[PASS] All folders created successfully")
    return config


def test_caption_reading():
    """Test caption file reading"""
    print("\n=== Test: Caption Reading ===")

    config = setup_test_environment()
    manager = InstagramWorkflowManager(config)

    # Create test image and caption
    test_image = config.drafts_folder / "test.jpg"
    test_caption = config.drafts_folder / "test.txt"

    test_image.write_text("fake image data")
    test_caption.write_text("Test caption with #hashtags")

    # Test caption reading
    caption = manager.read_caption(test_caption)
    assert caption == "Test caption with #hashtags", "Caption not read correctly"

    print(f"Caption read: {caption}")
    print("[PASS] Caption reading works")


def test_public_url_generation():
    """Test public URL generation"""
    print("\n=== Test: Public URL Generation ===")

    config = setup_test_environment()
    manager = InstagramWorkflowManager(config)

    # Create test image
    test_image = config.approved_folder / "test.jpg"
    test_image.write_text("fake image data")

    # Copy to public and get URL
    public_path, public_url = manager.copy_to_public(test_image)

    assert public_path.exists(), "Image not copied to Public folder"
    assert public_url == f"{config.public_url_base}/test.jpg", "Public URL incorrect"

    print(f"Public path: {public_path}")
    print(f"Public URL: {public_url}")
    print("[PASS] Public URL generation works")


def test_dry_run_processing():
    """Test dry run processing"""
    print("\n=== Test: Dry Run Processing ===")

    config = setup_test_environment()
    config.dry_run = True
    manager = InstagramWorkflowManager(config)

    # Create test image and caption
    test_image = config.approved_folder / "test.jpg"
    test_caption = config.approved_folder / "test.txt"

    test_image.write_text("fake image data")
    test_caption.write_text("Test caption for dry run")

    # Process image
    manager.process_image(test_image)

    # In dry run, files should still be in Approved
    assert test_image.exists(), "Image should still exist in Approved (dry run)"

    print("[PASS] Dry run processing works")


def test_file_lifecycle():
    """Test complete file lifecycle"""
    print("\n=== Test: File Lifecycle ===")

    config = setup_test_environment()
    manager = InstagramWorkflowManager(config)

    # Create test files in Drafts
    draft_image = config.drafts_folder / "lifecycle_test.jpg"
    draft_caption = config.drafts_folder / "lifecycle_test.txt"

    draft_image.write_text("fake image data")
    draft_caption.write_text("Lifecycle test caption")

    print("  1. Created files in Drafts/")

    # Move to Approved
    approved_image = config.approved_folder / "lifecycle_test.jpg"
    approved_caption = config.approved_folder / "lifecycle_test.txt"

    shutil.move(str(draft_image), str(approved_image))
    shutil.move(str(draft_caption), str(approved_caption))

    print("  2. Moved to Approved/")

    # Process (dry run)
    manager.process_image(approved_image)

    print("  3. Processed (dry run)")

    # Verify public copy exists
    public_image = config.public_folder / "lifecycle_test.jpg"
    assert public_image.exists(), "Image not copied to Public/"

    print("  4. Verified Public/ copy")
    print("[PASS] File lifecycle works")


def test_config_persistence():
    """Test configuration save/load"""
    print("\n=== Test: Configuration Persistence ===")

    config_file = "test_config_persistence.json"

    # Create and save config
    config1 = WorkflowConfig(config_file)
    config1.public_url_base = "https://test.ngrok.io"
    config1.save_config({
        "public_url_base": "https://test.ngrok.io",
        "auto_post": False
    })

    # Load config
    config2 = WorkflowConfig(config_file)

    assert config2.public_url_base == "https://test.ngrok.io", "Config not loaded correctly"

    # Cleanup
    Path(config_file).unlink()

    print("[PASS] Configuration persistence works")


def run_all_tests():
    """Run all workflow tests"""
    print("=" * 60)
    print("Instagram Workflow Manager - Test Suite")
    print("=" * 60)

    try:
        test_folder_creation()
        test_caption_reading()
        test_public_url_generation()
        test_dry_run_processing()
        test_file_lifecycle()
        test_config_persistence()

        print("\n" + "=" * 60)
        print("[SUCCESS] All workflow tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

    finally:
        cleanup_test_environment()

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
