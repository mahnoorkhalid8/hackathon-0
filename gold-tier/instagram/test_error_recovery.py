"""
Test script for Instagram Error Recovery System
Tests the "Ralph Wiggum" retry loop and error handling
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from error_recovery import InstagramErrorRecovery
from social_media_server import AuditLogger


def test_error_analysis():
    """Test error analysis for different error types"""
    print("\n=== Test: Error Analysis ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    # Test 400 - URL error
    error_400_url = {
        "success": False,
        "error": "Image could not be downloaded from URL",
        "error_code": 400
    }

    analysis = recovery.analyze_error(error_400_url)
    assert analysis['error_type'] == 'bad_request'
    assert analysis['recovery_action'] == 'check_public_url'
    assert analysis['is_recoverable'] == True
    print("  [PASS] 400 URL error analyzed correctly")

    # Test 400 - Caption too long
    error_400_caption = {
        "success": False,
        "error": "Caption is too long",
        "error_code": 400
    }

    analysis = recovery.analyze_error(error_400_caption)
    assert analysis['recovery_action'] == 'truncate_caption'
    assert analysis['is_recoverable'] == True
    print("  [PASS] 400 caption error analyzed correctly")

    # Test 401 - Token expired
    error_401 = {
        "success": False,
        "error": "Invalid OAuth access token",
        "error_code": 401
    }

    analysis = recovery.analyze_error(error_401)
    assert analysis['error_type'] == 'authentication_error'
    assert analysis['recovery_action'] == 'check_token_expiration'
    assert analysis['is_recoverable'] == False
    print("  [PASS] 401 auth error analyzed correctly")

    print("[PASS] Error analysis working correctly")


def test_caption_truncation():
    """Test caption truncation with hashtag preservation"""
    print("\n=== Test: Caption Truncation ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    # Test short caption (no truncation needed)
    short_caption = "Short caption #test"
    result = recovery.truncate_caption(short_caption)
    assert result == short_caption
    print("  [PASS] Short caption unchanged")

    # Test long caption with hashtags
    long_caption = "A" * 2500 + "\n\n#hashtag1 #hashtag2 #hashtag3"
    result = recovery.truncate_caption(long_caption, preserve_hashtags=True)
    assert len(result) <= recovery.CAPTION_MAX_LENGTH
    assert "#hashtag1" in result
    assert "#hashtag2" in result
    print(f"  [PASS] Long caption truncated to {len(result)} chars, hashtags preserved")

    # Test truncation without hashtag preservation
    result_no_preserve = recovery.truncate_caption(long_caption, preserve_hashtags=False)
    assert len(result_no_preserve) <= recovery.CAPTION_MAX_LENGTH
    print(f"  [PASS] Caption truncated without hashtag preservation")

    print("[PASS] Caption truncation working correctly")


def test_token_expiration_check():
    """Test token expiration checking"""
    print("\n=== Test: Token Expiration Check ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    # Test future date (not expired)
    is_expired, message = recovery.check_token_expiration("2026-12-31T00:00:00Z")
    assert not is_expired
    print(f"  [PASS] Future token: {message}")

    # Test past date (expired)
    is_expired, message = recovery.check_token_expiration("2020-01-01T00:00:00Z")
    assert is_expired
    print(f"  [PASS] Past token: {message}")

    print("[PASS] Token expiration check working correctly")


def test_should_retry():
    """Test retry decision logic"""
    print("\n=== Test: Retry Decision Logic ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    # Recoverable error, retry count 0
    error_analysis = {
        'is_recoverable': True,
        'recovery_action': 'truncate_caption'
    }

    should_retry = recovery.should_retry(error_analysis, 0)
    assert should_retry == True
    print("  [PASS] Should retry recoverable error (attempt 1)")

    # Recoverable error, retry count 1
    should_retry = recovery.should_retry(error_analysis, 1)
    assert should_retry == True
    print("  [PASS] Should retry recoverable error (attempt 2)")

    # Recoverable error, max retries reached
    should_retry = recovery.should_retry(error_analysis, 2)
    assert should_retry == False
    print("  [PASS] Should not retry after max attempts")

    # Non-recoverable error
    error_analysis['is_recoverable'] = False
    should_retry = recovery.should_retry(error_analysis, 0)
    assert should_retry == False
    print("  [PASS] Should not retry non-recoverable error")

    print("[PASS] Retry decision logic working correctly")


def test_error_note_creation():
    """Test error note generation"""
    print("\n=== Test: Error Note Creation ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    error_analysis = {
        'error_type': 'bad_request',
        'error_code': 400,
        'error_message': 'Caption is too long',
        'recovery_action': 'truncate_caption',
        'is_recoverable': True,
        'details': {}
    }

    original_caption = "A" * 2500
    note = recovery.create_error_note(error_analysis, 2, original_caption)

    assert "Instagram Posting Error Report" in note
    assert "bad_request" in note
    assert "2" in note  # retry count
    assert "NEXT STEPS" in note
    print("  [PASS] Error note contains required sections")

    # Check for specific guidance
    assert "Caption was too long" in note
    print("  [PASS] Error note contains specific guidance")

    print("[PASS] Error note creation working correctly")


def test_max_retries_constant():
    """Test MAX_RETRIES constant"""
    print("\n=== Test: MAX_RETRIES Constant ===")

    logger = AuditLogger("logs/test_recovery.json")
    recovery = InstagramErrorRecovery(logger)

    assert recovery.MAX_RETRIES == 2
    print(f"  [PASS] MAX_RETRIES = {recovery.MAX_RETRIES}")

    print("[PASS] MAX_RETRIES constant correct")


def run_all_tests():
    """Run all error recovery tests"""
    print("=" * 60)
    print("Instagram Error Recovery - Test Suite")
    print("=" * 60)

    try:
        test_error_analysis()
        test_caption_truncation()
        test_token_expiration_check()
        test_should_retry()
        test_error_note_creation()
        test_max_retries_constant()

        print("\n" + "=" * 60)
        print("[SUCCESS] All error recovery tests passed!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
