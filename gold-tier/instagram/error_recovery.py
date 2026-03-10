"""
Instagram Error Recovery Module
Implements self-healing retry logic with error analysis and recovery
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


class InstagramErrorRecovery:
    """
    Error recovery and self-healing for Instagram posting
    Implements the "Ralph Wiggum" loop - keep trying with smart recovery
    """

    # Instagram limits
    CAPTION_MAX_LENGTH = 2200
    MAX_RETRIES = 2

    def __init__(self, logger):
        self.logger = logger

    def analyze_error(self, error_response: Dict) -> Dict:
        """
        Analyze error response and determine recovery strategy

        Args:
            error_response: Error response from Instagram API

        Returns:
            Dict with error_type, error_code, message, and recovery_action
        """
        error_code = error_response.get("error_code", "unknown")
        error_message = error_response.get("error", "Unknown error")
        details = error_response.get("details", {})

        analysis = {
            "error_code": error_code,
            "error_message": error_message,
            "error_type": "unknown",
            "recovery_action": "none",
            "is_recoverable": False,
            "details": details
        }

        # Analyze by error code
        if isinstance(error_code, int):
            if error_code == 400:
                analysis["error_type"] = "bad_request"

                # Check specific 400 errors
                if "url" in error_message.lower() or "image" in error_message.lower():
                    analysis["recovery_action"] = "check_public_folder"
                    analysis["is_recoverable"] = True
                elif "caption" in error_message.lower() or "too long" in error_message.lower():
                    analysis["recovery_action"] = "truncate_caption"
                    analysis["is_recoverable"] = True
                else:
                    analysis["recovery_action"] = "log_and_move_to_drafts"

            elif error_code == 401:
                analysis["error_type"] = "authentication_error"
                analysis["recovery_action"] = "check_token_expiration"
                analysis["is_recoverable"] = False  # Requires manual intervention

            elif error_code == 403:
                analysis["error_type"] = "permission_denied"
                analysis["recovery_action"] = "log_critical"
                analysis["is_recoverable"] = False

            elif error_code >= 500:
                analysis["error_type"] = "server_error"
                analysis["recovery_action"] = "retry_later"
                analysis["is_recoverable"] = True

        # Check for specific error messages
        if "could not be downloaded" in error_message.lower():
            analysis["recovery_action"] = "check_public_url"
            analysis["is_recoverable"] = True
        elif "expired" in error_message.lower():
            analysis["recovery_action"] = "check_token_expiration"
            analysis["is_recoverable"] = False

        return analysis

    def truncate_caption(self, caption: str, preserve_hashtags: bool = True) -> str:
        """
        Truncate caption to Instagram's limit while preserving hashtags

        Args:
            caption: Original caption
            preserve_hashtags: Try to keep hashtags at the end

        Returns:
            Truncated caption
        """
        if len(caption) <= self.CAPTION_MAX_LENGTH:
            return caption

        if preserve_hashtags:
            # Try to find hashtags at the end
            lines = caption.split('\n')
            hashtag_lines = []
            content_lines = []

            for line in reversed(lines):
                if line.strip().startswith('#') or '#' in line:
                    hashtag_lines.insert(0, line)
                else:
                    content_lines.insert(0, line)
                    break

            # Add remaining lines to content
            for line in lines[:len(lines) - len(hashtag_lines) - len(content_lines)]:
                content_lines.append(line)

            # Reconstruct caption
            hashtags = '\n'.join(hashtag_lines)
            content = '\n'.join(content_lines)

            # Calculate available space
            available_space = self.CAPTION_MAX_LENGTH - len(hashtags) - 10  # Buffer for "...\n\n"

            if len(content) > available_space:
                content = content[:available_space] + "..."

            truncated = f"{content}\n\n{hashtags}".strip()
        else:
            truncated = caption[:self.CAPTION_MAX_LENGTH - 3] + "..."

        return truncated

    def check_token_expiration(self, expires_at: str) -> Tuple[bool, str]:
        """
        Check if token is expired

        Args:
            expires_at: Token expiration date

        Returns:
            Tuple of (is_expired, message)
        """
        from instagram_auth import InstagramAuth

        is_expired = InstagramAuth.is_token_expired(expires_at, buffer_days=0)

        if is_expired:
            return True, f"Token expired at {expires_at}. Refresh required."
        else:
            return False, f"Token valid until {expires_at}"

    def log_critical_error(self, error_type: str, error_message: str, context: Dict):
        """
        Log critical error for CEO briefing

        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        critical_log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": "CRITICAL",
            "component": "instagram_workflow",
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "requires_action": True
        }

        # Log to workflow logs
        self.logger.log(
            "critical_error",
            context,
            {"error": error_message, "type": error_type},
            "error"
        )

        # Also log to CEO briefing file if it exists
        ceo_log_path = Path("../logs/ceo_briefing.json")
        if ceo_log_path.parent.exists():
            try:
                if ceo_log_path.exists():
                    ceo_logs = json.loads(ceo_log_path.read_text())
                else:
                    ceo_logs = []

                ceo_logs.append(critical_log)
                ceo_log_path.write_text(json.dumps(ceo_logs, indent=2))
            except Exception as e:
                print(f"Warning: Could not write to CEO briefing log: {e}")

    def create_error_note(self, error_analysis: Dict, retry_count: int, original_caption: str = None) -> str:
        """
        Create detailed error note for manual review

        Args:
            error_analysis: Error analysis result
            retry_count: Number of retries attempted
            original_caption: Original caption if truncated

        Returns:
            Error note text
        """
        note = f"""Instagram Posting Error Report
Generated: {datetime.now().isoformat()}

ERROR DETAILS:
- Error Type: {error_analysis['error_type']}
- Error Code: {error_analysis['error_code']}
- Error Message: {error_analysis['error_message']}
- Retry Attempts: {retry_count}

RECOVERY ATTEMPTED:
- Recovery Action: {error_analysis['recovery_action']}
- Recoverable: {error_analysis['is_recoverable']}

WHAT HAPPENED:
The Instagram posting process attempted to post this content but encountered
an error that could not be automatically resolved after {retry_count} retries.

NEXT STEPS:
"""

        # Add specific guidance based on error type
        if error_analysis['error_type'] == 'authentication_error':
            note += """
1. Check token expiration: python cli.py status
2. Refresh token if needed: python cli.py refresh
3. Retry posting: python workflow_helper.py approve <image_name>
"""
        elif error_analysis['error_type'] == 'bad_request':
            if 'url' in error_analysis['error_message'].lower():
                note += """
1. Verify image is in Public/ folder
2. Check public server is running: python public_server.py
3. Verify public_url_base in workflow_config.json
4. Test URL accessibility in browser
5. Retry posting: python workflow_helper.py approve <image_name>
"""
            elif 'caption' in error_analysis['error_message'].lower():
                note += f"""
1. Caption was too long ({len(original_caption) if original_caption else 'unknown'} chars, max 2200)
2. Edit caption file to shorten it
3. Retry posting: python workflow_helper.py approve <image_name>
"""
                if original_caption:
                    note += f"\nORIGINAL CAPTION:\n{original_caption}\n"
        else:
            note += """
1. Review error message above
2. Check Instagram API status
3. Verify image meets Instagram requirements
4. Retry posting: python workflow_helper.py approve <image_name>
"""

        note += f"""
TECHNICAL DETAILS:
{json.dumps(error_analysis['details'], indent=2)}

This file was automatically generated by the Instagram Workflow Manager.
Delete this file after resolving the issue.
"""

        return note

    def should_retry(self, error_analysis: Dict, retry_count: int) -> bool:
        """
        Determine if we should retry based on error analysis

        Args:
            error_analysis: Error analysis result
            retry_count: Current retry count

        Returns:
            True if should retry
        """
        if retry_count >= self.MAX_RETRIES:
            return False

        return error_analysis['is_recoverable']
