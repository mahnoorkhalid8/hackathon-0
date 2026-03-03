"""
Validation Script - Silver Tier Digital FTE
Validates system configuration and readiness.
"""

import sys
from pathlib import Path
import yaml


def print_status(message: str, status: bool):
    """Print status with checkmark or X."""
    symbol = "[OK]" if status else "[FAIL]"
    print(f"  {symbol} {message}")


def validate_structure():
    """Validate directory structure."""
    print("\n[1] Validating Directory Structure...")

    required_dirs = [
        "memory",
        "memory/Inbox",
        "memory/Needs_Action",
        "memory/Needs_Approval",
        "memory/Done",
        "memory/SKILLS",
        "core",
        "watchers",
        "mcp",
        "scheduler",
        "logs",
        "config"
    ]

    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print_status(f"{dir_path}/", exists)
        all_exist = all_exist and exists

    return all_exist


def validate_config_files():
    """Validate configuration files."""
    print("\n[2] Validating Configuration Files...")

    config_files = [
        "config/fte_config.yaml",
        "config/approval_rules.yaml",
        "scheduler/schedule_config.yaml",
        "mcp/mcp_config.yaml",
        "watchers/watcher_config.yaml"
    ]

    all_valid = True
    for config_file in config_files:
        path = Path(config_file)
        exists = path.exists()

        if exists:
            try:
                with open(path, 'r') as f:
                    yaml.safe_load(f)
                print_status(f"{config_file} (valid YAML)", True)
            except Exception as e:
                print_status(f"{config_file} (invalid YAML: {e})", False)
                all_valid = False
        else:
            print_status(f"{config_file} (missing)", False)
            all_valid = False

    return all_valid


def validate_memory_vault():
    """Validate memory vault files."""
    print("\n[3] Validating Memory Vault...")

    memory_files = [
        "memory/Dashboard.md",
        "memory/Company_Handbook.md",
        "memory/Plan.md"
    ]

    all_exist = True
    for file_path in memory_files:
        exists = Path(file_path).exists()
        print_status(file_path, exists)
        all_exist = all_exist and exists

    return all_exist


def validate_skills():
    """Validate skill definitions."""
    print("\n[4] Validating Skills...")

    skills_path = Path("memory/SKILLS")
    if not skills_path.exists():
        print_status("SKILLS directory", False)
        return False

    skills = list(skills_path.glob("*.skill.md"))
    print_status(f"Found {len(skills)} skill(s)", len(skills) > 0)

    for skill in skills:
        print(f"    - {skill.name}")

    return len(skills) > 0


def validate_python_modules():
    """Validate Python modules can be imported."""
    print("\n[5] Validating Python Modules...")

    modules = [
        ("core.orchestrator", "Orchestrator"),
        ("core.context_loader", "ContextLoader"),
        ("core.reasoning_engine", "ReasoningEngine"),
        ("core.task_router", "TaskRouter"),
        ("core.state_manager", "StateManager"),
        ("core.executor", "Executor"),
        ("watchers.file_watcher", "FileWatcher"),
        ("watchers.time_watcher", "TimeWatcher"),
        ("mcp.mcp_client", "MCPClient")
    ]

    all_valid = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_status(f"{module_name}.{class_name}", True)
        except Exception as e:
            print_status(f"{module_name}.{class_name} ({e})", False)
            all_valid = False

    return all_valid


def validate_dependencies():
    """Validate Python dependencies."""
    print("\n[6] Validating Dependencies...")

    dependencies = [
        "yaml",
        "pathlib",
        "threading",
        "queue"
    ]

    all_valid = True
    for dep in dependencies:
        try:
            __import__(dep)
            print_status(dep, True)
        except ImportError:
            print_status(dep, False)
            all_valid = False

    # Check optional dependencies
    print("\n  Optional Dependencies:")
    optional = ["watchdog"]
    for dep in optional:
        try:
            __import__(dep)
            print_status(f"{dep} (optional)", True)
        except ImportError:
            print_status(f"{dep} (optional, not installed)", False)

    return all_valid


def validate_documentation():
    """Validate documentation files."""
    print("\n[7] Validating Documentation...")

    docs = [
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "PROJECT_SUMMARY.md",
        "CHANGELOG.md",
        "LICENSE"
    ]

    all_exist = True
    for doc in docs:
        exists = Path(doc).exists()
        print_status(doc, exists)
        all_exist = all_exist and exists

    return all_exist


def main():
    """Run all validations."""
    print("="*60)
    print("  Silver Tier Digital FTE - System Validation")
    print("="*60)

    results = {
        "Directory Structure": validate_structure(),
        "Configuration Files": validate_config_files(),
        "Memory Vault": validate_memory_vault(),
        "Skills": validate_skills(),
        "Python Modules": validate_python_modules(),
        "Dependencies": validate_dependencies(),
        "Documentation": validate_documentation()
    }

    print("\n" + "="*60)
    print("  Validation Summary")
    print("="*60 + "\n")

    all_passed = True
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[FAIL]"
        print(f"  {symbol} {check}: {status}")
        all_passed = all_passed and passed

    print("\n" + "="*60)
    if all_passed:
        print("  [OK] All validations passed!")
        print("  System is ready to use.")
        print("\n  Next steps:")
        print("    1. Install dependencies: pip install -r requirements.txt")
        print("    2. Run demo: python demo.py")
        print("    3. Start system: python main.py")
    else:
        print("  [FAIL] Some validations failed.")
        print("  Please review the errors above.")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
