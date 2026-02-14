"""
Test Suite for Human-in-the-Loop Approval System

Tests cover:
- Approval request creation
- Sensitive action detection
- Approval monitoring and decision reading
- Timeout and expiration handling
- File archiving
- Integration with TaskRouter and Executor

Author: Digital FTE System
Date: 2026-02-13
"""

import os
import sys
import time
import yaml
import shutil
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from approval_system import (
    ApprovalManager,
    ApprovalStatus,
    ActionType,
    ImpactLevel,
    Reversibility,
    ApprovalRequest,
    ApprovalDecision
)


class TestApprovalManager(unittest.TestCase):
    """Test suite for ApprovalManager class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary test directories
        self.test_dir = Path("test_approval_temp")
        self.test_dir.mkdir(exist_ok=True)

        self.vault_path = self.test_dir / "memory"
        self.vault_path.mkdir(exist_ok=True)

        self.template_path = self.test_dir / "templates"
        self.template_path.mkdir(exist_ok=True)

        # Test configuration
        self.config = {
            "vault_path": str(self.vault_path),
            "template_path": str(self.template_path),
            "poll_interval_seconds": 1,  # Fast polling for tests
            "default_timeout_seconds": 10,  # Short timeout for tests
            "company_domains": ["company.com", "testcompany.com"]
        }

        # Initialize ApprovalManager
        self.manager = ApprovalManager(self.config)

    def tearDown(self):
        """Clean up test environment after each test."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    # ========================================================================
    # Test: Sensitive Action Detection
    # ========================================================================

    def test_sensitive_action_email(self):
        """Test that email actions are detected as sensitive."""
        task = {
            "action_type": "send_email",
            "impact_level": "low",
            "data_sensitivity": "none",
            "reversibility": "irreversible"
        }

        result = self.manager.is_sensitive_action(task)
        self.assertTrue(result, "Email should be detected as sensitive")

    def test_sensitive_action_linkedin(self):
        """Test that LinkedIn posts are detected as sensitive."""
        task = {
            "action_type": "post_linkedin",
            "impact_level": "medium",
            "data_sensitivity": "none",
            "reversibility": "partially_reversible"
        }

        result = self.manager.is_sensitive_action(task)
        self.assertTrue(result, "LinkedIn post should be detected as sensitive")

    def test_sensitive_action_high_impact(self):
        """Test that high impact actions are detected as sensitive."""
        task = {
            "action_type": "api_call",
            "impact_level": "high",
            "data_sensitivity": "none",
            "reversibility": "reversible"
        }

        result = self.manager.is_sensitive_action(task)
        self.assertTrue(result, "High impact action should be detected as sensitive")

    def test_sensitive_action_pii_data(self):
        """Test that actions with PII are detected as sensitive."""
        task = {
            "action_type": "api_call",
            "impact_level": "low",
            "data_sensitivity": "pii",
            "reversibility": "reversible"
        }

        result = self.manager.is_sensitive_action(task)
        self.assertTrue(result, "PII data action should be detected as sensitive")

    def test_non_sensitive_action(self):
        """Test that safe actions are not detected as sensitive."""
        task = {
            "action_type": "read_file",
            "impact_level": "low",
            "data_sensitivity": "none",
            "reversibility": "reversible"
        }

        result = self.manager.is_sensitive_action(task)
        self.assertFalse(result, "Read file should not be detected as sensitive")

    # ========================================================================
    # Test: Policy Violation Detection
    # ========================================================================

    def test_policy_violation_pii_in_email(self):
        """Test detection of PII in email content."""
        task = {
            "action_type": "send_email",
            "content": "Please send payment to bank account 123456789",
            "recipients": ["user@company.com"]
        }

        result = self.manager._violates_policy(task)
        self.assertTrue(result, "Email with PII should violate policy")

    def test_policy_violation_external_recipient(self):
        """Test detection of external email recipients."""
        task = {
            "action_type": "send_email",
            "content": "Hello",
            "recipients": ["external@gmail.com"]
        }

        result = self.manager._violates_policy(task)
        self.assertTrue(result, "External recipient should violate policy")

    def test_policy_violation_high_amount_financial(self):
        """Test detection of high-value financial transactions."""
        task = {
            "action_type": "financial_transaction",
            "amount": 5000
        }

        result = self.manager._violates_policy(task)
        self.assertTrue(result, "High amount transaction should violate policy")

    def test_policy_compliant_internal_email(self):
        """Test that internal emails are policy compliant."""
        task = {
            "action_type": "send_email",
            "content": "Meeting at 3 PM",
            "recipients": ["colleague@company.com"]
        }

        result = self.manager._violates_policy(task)
        self.assertFalse(result, "Internal email should be policy compliant")

    # ========================================================================
    # Test: Approval Request Creation
    # ========================================================================

    def test_create_approval_request(self):
        """Test creation of approval request file."""
        task = {
            "action_type": "send_email",
            "title": "Test Email",
            "priority": "medium",
            "impact_level": "medium",
            "reversibility": "irreversible",
            "data_sensitivity": "none",
            "scope": "external",
            "requested_by": "test_agent"
        }

        action_details = {
            "description": "Test email description",
            "mcp_server": "email_server",
            "method": "send_email",
            "parameters": {"to": "test@example.com"},
            "context": "Test context",
            "reasoning": "Test reasoning",
            "expected_outcome": "Test outcome",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)

        # Verify approval ID format
        self.assertTrue(approval_id.startswith("APR-"))
        self.assertIn("-", approval_id)

        # Verify file was created
        file_path = self.manager.needs_approval_path / f"{approval_id}.md"
        self.assertTrue(file_path.exists(), "Approval file should be created")

        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("status: \"PENDING\"", content)
        self.assertIn("Test Email", content)
        self.assertIn("email_server", content)

    def test_approval_id_uniqueness(self):
        """Test that approval IDs are unique."""
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        # Create multiple approval requests
        id1 = self.manager.create_approval_request(task, action_details)
        id2 = self.manager.create_approval_request(task, action_details)
        id3 = self.manager.create_approval_request(task, action_details)

        # Verify all IDs are unique
        self.assertNotEqual(id1, id2)
        self.assertNotEqual(id2, id3)
        self.assertNotEqual(id1, id3)

    # ========================================================================
    # Test: Approval Decision Reading
    # ========================================================================

    def test_read_pending_approval(self):
        """Test reading a pending approval status."""
        # Create approval request
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)
        file_path = self.manager.needs_approval_path / f"{approval_id}.md"

        # Read decision
        decision = self.manager._read_approval_decision(file_path)

        self.assertEqual(decision.status, ApprovalStatus.PENDING)

    def test_read_approved_decision(self):
        """Test reading an approved decision."""
        # Create approval request
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)
        file_path = self.manager.needs_approval_path / f"{approval_id}.md"

        # Simulate human approval
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('status: "PENDING"', 'status: "APPROVED"')
        content = content.replace(
            'decided_by: "{{APPROVER_NAME}}"',
            'decided_by: "test_human"'
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Read decision
        decision = self.manager._read_approval_decision(file_path)

        self.assertEqual(decision.status, ApprovalStatus.APPROVED)

    # ========================================================================
    # Test: Approval Monitoring
    # ========================================================================

    def test_monitor_approval_timeout(self):
        """Test that monitoring times out correctly."""
        # Create approval request
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)

        # Monitor with short timeout (3 seconds)
        start_time = time.time()
        status, decision = self.manager.monitor_approval(approval_id, timeout_seconds=3)
        elapsed = time.time() - start_time

        # Verify timeout occurred
        self.assertEqual(status, ApprovalStatus.EXPIRED)
        self.assertGreaterEqual(elapsed, 3)
        self.assertLess(elapsed, 5)  # Should not take much longer than timeout

    def test_monitor_approval_approved(self):
        """Test monitoring detects approval."""
        # Create approval request
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)
        file_path = self.manager.needs_approval_path / f"{approval_id}.md"

        # Simulate human approval after 2 seconds
        def approve_after_delay():
            time.sleep(2)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('status: "PENDING"', 'status: "APPROVED"')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        import threading
        approval_thread = threading.Thread(target=approve_after_delay)
        approval_thread.start()

        # Monitor (should detect approval)
        status, decision = self.manager.monitor_approval(approval_id, timeout_seconds=10)

        approval_thread.join()

        self.assertEqual(status, ApprovalStatus.APPROVED)

    # ========================================================================
    # Test: File Archiving
    # ========================================================================

    def test_archive_approval(self):
        """Test archiving approval to Done directory."""
        # Create approval request
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        approval_id = self.manager.create_approval_request(task, action_details)

        # Archive
        self.manager._archive_approval(approval_id, "EXECUTED")

        # Verify file moved
        source_path = self.manager.needs_approval_path / f"{approval_id}.md"
        dest_path = self.manager.done_path / f"{approval_id}-EXECUTED.md"

        self.assertFalse(source_path.exists(), "Source file should be removed")
        self.assertTrue(dest_path.exists(), "Destination file should exist")

    # ========================================================================
    # Test: Get Pending Approvals
    # ========================================================================

    def test_get_pending_approvals(self):
        """Test retrieving list of pending approvals."""
        # Create multiple approval requests
        task = {
            "action_type": "send_email",
            "title": "Test",
            "priority": "low",
            "impact_level": "low",
            "reversibility": "reversible",
            "data_sensitivity": "none"
        }

        action_details = {
            "description": "Test",
            "mcp_server": "test",
            "method": "test",
            "parameters": {},
            "context": "",
            "reasoning": "",
            "expected_outcome": "",
            "risks": [],
            "safeguards": [],
            "policy_status": "compliant"
        }

        id1 = self.manager.create_approval_request(task, action_details)
        id2 = self.manager.create_approval_request(task, action_details)
        id3 = self.manager.create_approval_request(task, action_details)

        # Get pending approvals
        pending = self.manager.get_pending_approvals()

        self.assertEqual(len(pending), 3)
        self.assertTrue(any(p["id"] == id1 for p in pending))
        self.assertTrue(any(p["id"] == id2 for p in pending))
        self.assertTrue(any(p["id"] == id3 for p in pending))


# ============================================================================
# Run Tests
# ============================================================================

def run_tests():
    """Run all tests and display results."""
    print("=" * 70)
    print("  Human-in-the-Loop Approval System - Test Suite")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestApprovalManager)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    print("  Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("[OK] All tests passed!")
        return 0
    else:
        print("[FAIL] Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
