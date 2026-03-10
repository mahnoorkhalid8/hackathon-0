"""
Test script for Instagram Business API integration
Tests authentication, posting, and insights retrieval
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from instagram_auth import InstagramAuth, save_credentials_to_env
from social_media_server import post_instagram_image, get_instagram_insights

# Load environment
load_dotenv("../.env")

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def test_token_expiration_check():
    """Test token expiration checking"""
    print("\n=== Testing Token Expiration Check ===")

    # Test with future date (not expired)
    future_date = "2026-12-31T00:00:00Z"
    is_expired = InstagramAuth.is_token_expired(future_date)
    print(f"Future date {future_date}: {'EXPIRED' if is_expired else 'VALID'}")
    assert not is_expired, "Future token should not be expired"

    # Test with past date (expired)
    past_date = "2020-01-01T00:00:00Z"
    is_expired = InstagramAuth.is_token_expired(past_date)
    print(f"Past date {past_date}: {'EXPIRED' if is_expired else 'VALID'}")
    assert is_expired, "Past token should be expired"

    # Test with near-expiry date (within 7 days)
    near_expiry = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat().replace("+00:00", "Z")
    is_expired = InstagramAuth.is_token_expired(near_expiry)
    print(f"Near expiry {near_expiry}: {'EXPIRED' if is_expired else 'VALID'}")
    assert is_expired, "Token expiring in 5 days should be considered expired (7-day buffer)"

    print("[PASS] Token expiration checks passed")
    return True


def test_credentials_loaded():
    """Test that credentials are loaded from environment"""
    print("\n=== Testing Credentials ===")

    business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    expires_at = os.getenv("IG_TOKEN_EXPIRES_AT")

    print(f"Business ID: {business_id}")
    print(f"Access Token: {access_token[:20]}..." if access_token else "Access Token: None")
    print(f"Expires At: {expires_at}")

    if not business_id or not access_token:
        print("[WARN] Instagram credentials not found in .env file")
        return False

    # Check if token is expired
    if expires_at:
        is_expired = InstagramAuth.is_token_expired(expires_at)
        if is_expired:
            print("[WARN] Access token is expired or will expire soon")
            print("       Run token refresh flow to get a new token")
        else:
            print("[PASS] Access token is valid")

    print("[PASS] Credentials loaded successfully")
    return True


def test_auth_initialization():
    """Test authentication manager initialization"""
    print("\n=== Testing Auth Initialization ===")

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", "https://localhost/")

    if not app_id or not app_secret:
        print("[WARN] Facebook app credentials not found")
        return False

    try:
        auth = InstagramAuth(app_id, app_secret, redirect_uri)
        print(f"Auth manager initialized with App ID: {app_id}")
        print(f"Redirect URI: {redirect_uri}")
        print("[PASS] Auth initialization successful")
        return True
    except Exception as e:
        print(f"[FAIL] Auth initialization failed: {e}")
        return False


def test_post_image_dry_run():
    """Test image posting function (dry run - checks setup only)"""
    print("\n=== Testing Image Post Setup ===")

    business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not business_id or not access_token:
        print("[WARN] Skipping: Credentials not available")
        return False

    print("Setup validated:")
    print(f"  - Business ID: {business_id}")
    print(f"  - Token available: Yes")
    print(f"  - Logs directory: logs/")

    # Check if logs directory exists
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("  - Created logs directory")

    print("[PASS] Image posting setup ready")
    print("\nTo test actual posting, use:")
    print('  result = post_instagram_image("https://example.com/image.jpg", "Test caption")')
    return True


def test_audit_logging():
    """Test audit logging functionality"""
    print("\n=== Testing Audit Logging ===")

    from social_media_server import AuditLogger

    logger = AuditLogger()

    # Test log entry
    logger.log(
        tool_name="test_operation",
        input_data={"test": "input"},
        response_data={"status": "success"},
        status="success"
    )

    # Verify log file exists
    log_file = Path("logs/instagram_logs.json")
    if log_file.exists():
        logs = json.loads(log_file.read_text())
        print(f"Log file exists with {len(logs)} entries")
        print(f"Latest entry: {logs[-1]['tool']}")
        print("[PASS] Audit logging working")
        return True
    else:
        print("[FAIL] Log file not created")
        return False


def test_mcp_server_import():
    """Test MCP server imports"""
    print("\n=== Testing MCP Server ===")

    try:
        from mcp.server import Server
        print("[PASS] MCP library installed")
        return True
    except ImportError:
        print("[WARN] MCP library not installed")
        print("       Install with: pip install mcp")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Instagram Business API Integration - Test Suite")
    print("=" * 60)

    results = {
        "Token Expiration Check": test_token_expiration_check(),
        "Credentials Loaded": test_credentials_loaded(),
        "Auth Initialization": test_auth_initialization(),
        "Image Post Setup": test_post_image_dry_run(),
        "Audit Logging": test_audit_logging(),
        "MCP Server Import": test_mcp_server_import()
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[WARN/SKIP]"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARN] Some tests failed or were skipped")
        print("Check warnings above for details")


if __name__ == "__main__":
    run_all_tests()
