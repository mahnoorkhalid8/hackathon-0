"""
Test script for CEO Briefing System
Tests report generation, metrics calculation, and system health checks
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent))

from ceo_briefing import CEOBriefingGenerator


def test_initialization():
    """Test CEO briefing generator initialization"""
    print("\n=== Test: Initialization ===")

    try:
        generator = CEOBriefingGenerator()
        assert generator.business_id is not None
        assert generator.access_token is not None
        print(f"  [PASS] Initialized with Business ID: {generator.business_id}")
        return True
    except Exception as e:
        print(f"  [FAIL] Initialization failed: {e}")
        return False


def test_system_health_check():
    """Test system health monitoring"""
    print("\n=== Test: System Health Check ===")

    try:
        generator = CEOBriefingGenerator()
        health = generator.check_system_health()

        assert "status" in health
        assert "issues" in health
        assert "warnings" in health

        print(f"  System Status: {health['status']}")
        print(f"  Issues: {len(health['issues'])}")
        print(f"  Warnings: {len(health['warnings'])}")

        if health['status'] == 'healthy':
            print("  [PASS] System is healthy")
        elif health['status'] == 'warning':
            print("  [PASS] System has warnings (expected)")
            for warning in health['warnings']:
                print(f"    - {warning['type']}: {warning['message']}")
        else:
            print("  [WARN] System has critical issues")
            for issue in health['issues']:
                print(f"    - {issue['type']}: {issue['message']}")

        return True
    except Exception as e:
        print(f"  [FAIL] Health check failed: {e}")
        return False


def test_metrics_calculation():
    """Test metrics calculation"""
    print("\n=== Test: Metrics Calculation ===")

    try:
        generator = CEOBriefingGenerator()

        # Mock media data
        mock_media = [
            {
                "id": "1",
                "insights": {
                    "impressions": 1000,
                    "reach": 800,
                    "engagement": 50,
                    "saved": 5
                }
            },
            {
                "id": "2",
                "insights": {
                    "impressions": 1500,
                    "reach": 1200,
                    "engagement": 75,
                    "saved": 8
                }
            }
        ]

        metrics = generator.calculate_metrics(mock_media)

        assert metrics['total_posts'] == 2
        assert metrics['total_impressions'] == 2500
        assert metrics['total_reach'] == 2000
        assert metrics['total_engagement'] == 125
        assert metrics['total_saved'] == 13
        assert metrics['total_cost'] == 10.00  # 2 posts * $5
        assert metrics['cost_per_engagement'] == 0.08  # $10 / 125

        print(f"  [PASS] Total Posts: {metrics['total_posts']}")
        print(f"  [PASS] Total Impressions: {metrics['total_impressions']}")
        print(f"  [PASS] Total Engagement: {metrics['total_engagement']}")
        print(f"  [PASS] Cost per Engagement: ${metrics['cost_per_engagement']:.4f}")
        print(f"  [PASS] Engagement Rate: {metrics['engagement_rate']:.2f}%")

        return True
    except Exception as e:
        print(f"  [FAIL] Metrics calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_top_post_selection():
    """Test top post selection"""
    print("\n=== Test: Top Post Selection ===")

    try:
        generator = CEOBriefingGenerator()

        # Mock media data
        mock_media = [
            {
                "id": "1",
                "caption": "Post 1",
                "insights": {"engagement": 50}
            },
            {
                "id": "2",
                "caption": "Post 2 - Top",
                "insights": {"engagement": 150}
            },
            {
                "id": "3",
                "caption": "Post 3",
                "insights": {"engagement": 75}
            }
        ]

        top_post = generator.find_top_post(mock_media)

        assert top_post is not None
        assert top_post['id'] == "2"
        assert top_post['insights']['engagement'] == 150

        print(f"  [PASS] Top post identified: {top_post['caption']}")
        print(f"  [PASS] Engagement: {top_post['insights']['engagement']}")

        return True
    except Exception as e:
        print(f"  [FAIL] Top post selection failed: {e}")
        return False


def test_report_generation():
    """Test report generation (dry run)"""
    print("\n=== Test: Report Generation ===")

    try:
        generator = CEOBriefingGenerator()

        # Note: This will make actual API calls
        print("  Generating report (this may take a moment)...")
        report = generator.generate_markdown_report(days=7)

        assert "Instagram Business - CEO Briefing" in report
        assert "Executive Summary" in report
        assert "Performance Metrics" in report
        assert "Marketing Investment" in report

        print(f"  [PASS] Report generated successfully")
        print(f"  [PASS] Report length: {len(report)} characters")

        # Check for key sections
        sections = [
            "Executive Summary",
            "Performance Metrics",
            "Marketing Investment",
            "Recommendations"
        ]

        for section in sections:
            if section in report:
                print(f"  [PASS] Section found: {section}")
            else:
                print(f"  [WARN] Section missing: {section}")

        return True
    except Exception as e:
        print(f"  [FAIL] Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_saving():
    """Test report saving to file"""
    print("\n=== Test: Report Saving ===")

    try:
        generator = CEOBriefingGenerator()

        # Create a simple test report
        test_report = "# Test Report\n\nThis is a test."

        report_path = generator.save_report(test_report, "test_report.md")

        assert report_path.exists()
        assert report_path.read_text(encoding='utf-8') == test_report

        print(f"  [PASS] Report saved to: {report_path}")

        # Cleanup
        report_path.unlink()
        print(f"  [PASS] Test file cleaned up")

        return True
    except Exception as e:
        print(f"  [FAIL] Report saving failed: {e}")
        return False


def test_cost_per_post_constant():
    """Test COST_PER_POST constant"""
    print("\n=== Test: Cost per Post Constant ===")

    generator = CEOBriefingGenerator()

    assert generator.COST_PER_POST == 5.00
    print(f"  [PASS] COST_PER_POST = ${generator.COST_PER_POST:.2f}")

    return True


def run_all_tests():
    """Run all CEO briefing tests"""
    print("=" * 60)
    print("CEO Briefing System - Test Suite")
    print("=" * 60)

    results = {
        "Initialization": test_initialization(),
        "System Health Check": test_system_health_check(),
        "Metrics Calculation": test_metrics_calculation(),
        "Top Post Selection": test_top_post_selection(),
        "Report Saving": test_report_saving(),
        "Cost per Post Constant": test_cost_per_post_constant(),
        "Report Generation": test_report_generation()  # Last (makes API calls)
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n" + "=" * 60)
        print("[SUCCESS] All CEO briefing tests passed!")
        print("=" * 60)
        return True
    else:
        print("\n[WARN] Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
