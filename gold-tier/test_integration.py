"""
Integration Test - Silver Tier Digital FTE
Tests the complete system workflow end-to-end.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Test imports
print("[Test] Testing imports...")
try:
    from core import Orchestrator, ContextLoader, ReasoningEngine, TaskRouter, StateManager, Executor
    from watchers import FileWatcher, TimeWatcher
    from mcp import MCPClient
    print("[Test] All imports successful")
except Exception as e:
    print(f"[Test] Import failed: {e}")
    sys.exit(1)


def test_context_loader():
    """Test context loader functionality."""
    print("\n[Test] Testing Context Loader...")

    try:
        import yaml
        with open("config/fte_config.yaml", 'r') as f:
            config = yaml.safe_load(f)

        loader = ContextLoader(config)

        # Test loading dashboard
        dashboard = loader.load_dashboard()
        assert "Dashboard" in dashboard, "Dashboard should contain title"
        print("  [OK] Dashboard loaded")

        # Test loading handbook
        handbook = loader.load_handbook()
        assert "Handbook" in handbook, "Handbook should contain title"
        print("  [OK] Handbook loaded")

        # Test loading skills
        skills = loader.list_skills()
        assert len(skills) >= 3, "Should have at least 3 skills"
        print(f"  [OK] Found {len(skills)} skills")

        # Test loading a specific skill
        skill = loader.load_skill("email_responder")
        assert skill is not None, "Should load email_responder skill"
        print("  [OK] Skill loading works")

        return True
    except Exception as e:
        print(f"  [FAIL] Context loader test failed: {e}")
        return False


def test_reasoning_engine():
    """Test reasoning engine functionality."""
    print("\n[Test] Testing Reasoning Engine...")

    try:
        import yaml
        with open("config/fte_config.yaml", 'r') as f:
            config = yaml.safe_load(f)

        engine = ReasoningEngine(config)

        # Create a test event
        test_event = {
            'type': 'test_event',
            'source': 'integration_test',
            'timestamp': datetime.now().isoformat(),
            'payload': {'test': 'data'}
        }

        # Create test context
        context = {
            'event': test_event,
            'dashboard': 'Test dashboard',
            'handbook': 'Test handbook',
            'skill_definition': 'Test skill'
        }

        # Run reasoning
        result = engine.analyze_event(context)

        assert 'situation' in result, "Should have situation"
        assert 'analysis' in result, "Should have analysis"
        assert 'decision' in result, "Should have decision"
        assert 'confidence' in result, "Should have confidence"

        print(f"  [OK] Reasoning completed with {result['confidence']}% confidence")
        print(f"  [OK] Decision: {result['decision']['action']}")

        return True
    except Exception as e:
        print(f"  [FAIL] Reasoning engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_router():
    """Test task router functionality."""
    print("\n[Test] Testing Task Router...")

    try:
        import yaml
        with open("config/fte_config.yaml", 'r') as f:
            config = yaml.safe_load(f)

        router = TaskRouter(config)

        # Create test event and reasoning
        test_event = {
            'type': 'test_event',
            'source': 'integration_test',
            'timestamp': datetime.now().isoformat(),
            'payload': {'test': 'data'}
        }

        test_reasoning = {
            'situation': 'Test situation',
            'analysis': ['Step 1', 'Step 2'],
            'decision': {'action': 'test', 'reason': 'testing'},
            'confidence': 85,
            'requires_approval': False
        }

        # Route task
        task_file = router.route_task(test_event, test_reasoning)

        assert task_file.exists(), "Task file should be created"
        print(f"  [OK] Task routed to: {task_file}")

        # Clean up
        task_file.unlink()

        return True
    except Exception as e:
        print(f"  [FAIL] Task router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_client():
    """Test MCP client functionality."""
    print("\n[Test] Testing MCP Client...")

    try:
        client = MCPClient()

        # List servers
        servers = client.list_servers()
        print(f"  [OK] Found {len(servers)} MCP servers configured")

        # Test simulated call
        result = client.call('web_search', 'search', {'query': 'test'})
        assert 'success' in result, "Should have success field"
        print(f"  [OK] MCP call simulation works")

        return True
    except Exception as e:
        print(f"  [FAIL] MCP client test failed: {e}")
        return False


def test_state_manager():
    """Test state manager functionality."""
    print("\n[Test] Testing State Manager...")

    try:
        import yaml
        with open("config/fte_config.yaml", 'r') as f:
            config = yaml.safe_load(f)

        manager = StateManager(config)

        # Test dashboard update
        test_metrics = {
            'completed_today': 5,
            'tasks_processed': 10,
            'auto_approved': 7,
            'required_approval': 3,
            'recent_activity': ['Test activity 1', 'Test activity 2'],
            'health': 'Healthy'
        }

        manager.update_dashboard(test_metrics)

        # Verify dashboard was updated
        dashboard_file = Path("memory/Dashboard.md")
        assert dashboard_file.exists(), "Dashboard should exist"

        content = dashboard_file.read_text()
        assert "Completed Today: 5" in content, "Should show completed count"

        print("  [OK] Dashboard update works")

        return True
    except Exception as e:
        print(f"  [FAIL] State manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files and directories exist."""
    print("\n[Test] Testing File Structure...")

    required_paths = [
        "memory/Dashboard.md",
        "memory/Company_Handbook.md",
        "memory/Plan.md",
        "memory/SKILLS/email_responder.skill.md",
        "core/orchestrator.py",
        "watchers/file_watcher.py",
        "config/fte_config.yaml",
        "main.py",
        "README.md"
    ]

    all_exist = True
    for path in required_paths:
        exists = Path(path).exists()
        if not exists:
            print(f"  [FAIL] Missing: {path}")
            all_exist = False

    if all_exist:
        print(f"  [OK] All {len(required_paths)} required files exist")

    return all_exist


def main():
    """Run all integration tests."""
    print("="*60)
    print("  Silver Tier Digital FTE - Integration Tests")
    print("="*60)

    tests = [
        ("File Structure", test_file_structure),
        ("Context Loader", test_context_loader),
        ("Reasoning Engine", test_reasoning_engine),
        ("Task Router", test_task_router),
        ("MCP Client", test_mcp_client),
        ("State Manager", test_state_manager)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[Test] {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60 + "\n")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"  {symbol} {test_name}: {status}")

    print(f"\n  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  [OK] All integration tests passed!")
        print("  System is fully functional and ready for use.")
    else:
        print(f"\n  [FAIL] {total - passed} test(s) failed.")
        print("  Please review the errors above.")

    print("="*60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
