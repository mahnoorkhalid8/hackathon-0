"""
Demo: Iterative Reasoning Engine
Demonstrates the engine executing a task step-by-step with plan updates.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from iterative_reasoning_engine import IterativeReasoningEngine, Plan


def demo_simple_task():
    """Demonstrate a simple task execution."""
    print("="*70)
    print("  DEMO 1: Simple Task Execution")
    print("="*70 + "\n")

    # Initialize engine
    config = {
        'plans_dir': 'memory/plans'
    }
    engine = IterativeReasoningEngine(config)

    # Define a simple task
    task = {
        'objective': 'Generate a daily status report',
        'description': 'Create a summary of today\'s activities',
        'priority': 'MEDIUM',
        'success_criteria': [
            'Data collected from all sources',
            'Report generated in markdown format',
            'Quality checks passed'
        ],
        'steps': [
            {
                'name': 'Collect Data',
                'description': 'Gather activity data from logs',
                'actions': ['read_logs', 'parse_events', 'aggregate_data'],
                'expected_outputs': ['activity_data.json']
            },
            {
                'name': 'Generate Report',
                'description': 'Create formatted report',
                'actions': ['load_template', 'populate_data', 'format_markdown'],
                'expected_outputs': ['daily_report.md'],
                'dependencies': ['step-001']
            },
            {
                'name': 'Quality Check',
                'description': 'Verify report completeness',
                'actions': ['check_format', 'verify_data', 'validate_output'],
                'expected_outputs': ['quality_report.txt'],
                'dependencies': ['step-002']
            }
        ]
    }

    # Create plan
    print("[Demo] Creating execution plan...")
    plan = engine.analyze_and_create_plan(task)
    print(f"[Demo] Plan created: {plan.id}")
    print(f"[Demo] Objective: {plan.objective}")
    print(f"[Demo] Steps: {len(plan.steps)}")
    print()

    # Execute plan
    print("[Demo] Executing plan iteratively...")
    print()
    result = engine.execute_plan_iteratively(plan)

    # Show results
    print("\n" + "="*70)
    print("  EXECUTION RESULTS")
    print("="*70 + "\n")
    print(f"Plan Status: {result.status.value}")
    print(f"Completed Steps: {sum(1 for s in result.steps if s.status.value == 'COMPLETED')}/{len(result.steps)}")
    print(f"Total Time: {(result.completed_at - result.created_at).total_seconds():.1f}s")
    print()

    # Show step details
    print("Step Details:")
    for step in result.steps:
        status_symbol = "[OK]" if step.status.value == "COMPLETED" else "[FAIL]"
        print(f"  {status_symbol} {step.id}: {step.name} - {step.status.value}")

    print(f"\nPlan file: memory/plans/{plan.id}.md")
    print()


def demo_complex_task_with_failure():
    """Demonstrate a complex task with failure and recovery."""
    print("="*70)
    print("  DEMO 2: Complex Task with Failure Recovery")
    print("="*70 + "\n")

    # Initialize engine
    config = {
        'plans_dir': 'memory/plans'
    }
    engine = IterativeReasoningEngine(config)

    # Define a complex task
    task = {
        'objective': 'Generate weekly sales report with trend analysis',
        'priority': 'HIGH',
        'deadline': '2026-02-13 17:00:00',
        'success_criteria': [
            'Sales data retrieved from all regions',
            'Data validated and cleaned',
            'Trend analysis completed',
            'Report generated and reviewed'
        ],
        'resources': [
            'Regional databases (US, EU, APAC)',
            'Historical data (12 months)',
            'Report template'
        ],
        'constraints': [
            'Must complete before 5 PM',
            'Report must be under 5 pages',
            'All data must be anonymized'
        ],
        'steps': [
            {
                'name': 'Fetch Sales Data',
                'description': 'Retrieve sales data from regional databases',
                'actions': [
                    'connect_to_us_db',
                    'connect_to_eu_db',
                    'connect_to_apac_db',
                    'execute_queries',
                    'export_to_csv'
                ],
                'expected_outputs': ['sales_us.csv', 'sales_eu.csv', 'sales_apac.csv'],
                'is_critical': True
            },
            {
                'name': 'Validate and Clean Data',
                'description': 'Check data quality and clean',
                'actions': [
                    'load_data',
                    'check_missing_values',
                    'remove_duplicates',
                    'standardize_formats',
                    'convert_currencies'
                ],
                'expected_outputs': ['sales_clean.csv', 'quality_report.txt'],
                'dependencies': ['step-001'],
                'is_critical': True
            },
            {
                'name': 'Perform Trend Analysis',
                'description': 'Analyze trends and generate insights',
                'actions': [
                    'calculate_metrics',
                    'compare_periods',
                    'identify_patterns',
                    'detect_anomalies',
                    'generate_charts'
                ],
                'expected_outputs': ['metrics.json', 'charts/'],
                'dependencies': ['step-002'],
                'is_critical': True
            },
            {
                'name': 'Generate Report',
                'description': 'Create formatted report document',
                'actions': [
                    'load_template',
                    'insert_summary',
                    'add_metrics',
                    'embed_charts',
                    'format_document'
                ],
                'expected_outputs': ['weekly_report.md', 'weekly_report.pdf'],
                'dependencies': ['step-003'],
                'is_critical': True
            },
            {
                'name': 'Quality Check',
                'description': 'Review and validate report',
                'actions': [
                    'verify_charts',
                    'check_calculations',
                    'spell_check',
                    'verify_page_count'
                ],
                'expected_outputs': ['quality_check.txt'],
                'dependencies': ['step-004'],
                'is_critical': False
            }
        ]
    }

    # Create plan
    print("[Demo] Creating execution plan for complex task...")
    plan = engine.analyze_and_create_plan(task)
    print(f"[Demo] Plan created: {plan.id}")
    print(f"[Demo] Objective: {plan.objective}")
    print(f"[Demo] Steps: {len(plan.steps)}")
    print(f"[Demo] Critical steps: {sum(1 for s in plan.steps if s.is_critical)}")
    print()

    # Execute plan
    print("[Demo] Executing plan iteratively...")
    print("[Demo] (This will show step-by-step progress)")
    print()

    result = engine.execute_plan_iteratively(plan)

    # Show results
    print("\n" + "="*70)
    print("  EXECUTION RESULTS")
    print("="*70 + "\n")
    print(f"Plan Status: {result.status.value}")
    print(f"Completed Steps: {sum(1 for s in result.steps if s.status.value == 'COMPLETED')}/{len(result.steps)}")

    if result.completed_at:
        duration = (result.completed_at - result.created_at).total_seconds()
        print(f"Total Time: {duration:.1f}s")

    print()

    # Show detailed step information
    print("Detailed Step Information:")
    print()
    for step in result.steps:
        status_map = {
            'COMPLETED': '[OK]',
            'FAILED': '[FAIL]',
            'PENDING': '[PEND]',
            'IN_PROGRESS': '[PROG]',
            'SKIPPED': '[SKIP]'
        }
        symbol = status_map.get(step.status.value, '[?]')

        print(f"{symbol} {step.id}: {step.name}")
        print(f"   Status: {step.status.value}")
        print(f"   Attempts: {step.attempts}/{step.max_attempts}")

        if step.started_at and step.completed_at:
            duration = (step.completed_at - step.started_at).total_seconds()
            print(f"   Duration: {duration:.2f}s")

        if step.notes:
            print(f"   Notes: {step.notes[:100]}...")

        print()

    print(f"Plan file: memory/plans/{plan.id}.md")
    print()


def demo_auto_generated_plan():
    """Demonstrate automatic plan generation from objective."""
    print("="*70)
    print("  DEMO 3: Auto-Generated Plan from Objective")
    print("="*70 + "\n")

    # Initialize engine
    config = {
        'plans_dir': 'memory/plans'
    }
    engine = IterativeReasoningEngine(config)

    # Define task with just objective (no explicit steps)
    task = {
        'objective': 'Analyze customer feedback data and generate insights report',
        'priority': 'HIGH',
        'success_criteria': [
            'All feedback data processed',
            'Sentiment analysis completed',
            'Key themes identified',
            'Insights report generated'
        ]
    }

    # Create plan (engine will auto-generate steps)
    print("[Demo] Creating plan from objective only...")
    print(f"[Demo] Objective: {task['objective']}")
    print("[Demo] Engine will automatically decompose into steps...")
    print()

    plan = engine.analyze_and_create_plan(task)

    print(f"[Demo] Plan created: {plan.id}")
    print(f"[Demo] Auto-generated {len(plan.steps)} steps:")
    print()

    for step in plan.steps:
        print(f"  {step.id}: {step.name}")
        print(f"    Description: {step.description}")
        print(f"    Actions: {', '.join(step.actions)}")
        if step.dependencies:
            print(f"    Dependencies: {', '.join(step.dependencies)}")
        print()

    # Execute
    print("[Demo] Executing auto-generated plan...")
    print()

    result = engine.execute_plan_iteratively(plan)

    print("\n" + "="*70)
    print("  RESULTS")
    print("="*70 + "\n")
    print(f"Status: {result.status.value}")
    print(f"Completed: {sum(1 for s in result.steps if s.status.value == 'COMPLETED')}/{len(result.steps)}")
    print(f"\nPlan file: memory/plans/{plan.id}.md")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("=" * 70)
    print("  Iterative Reasoning Engine - Demonstration")
    print("=" * 70)
    print("\n")

    demos = [
        ("Simple Task", demo_simple_task),
        ("Complex Task with Failure Recovery", demo_complex_task_with_failure),
        ("Auto-Generated Plan", demo_auto_generated_plan)
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n[Demo {i}/{len(demos)}] {name}")
        print()

        try:
            demo_func()
        except Exception as e:
            print(f"\n[Error] Demo failed: {e}")
            import traceback
            traceback.print_exc()

        if i < len(demos):
            print("\n" + "-"*70)
            print("  Press Enter to continue to next demo...")
            print("-"*70)
            input()

    print("\n" + "="*70)
    print("  All Demos Complete!")
    print("="*70)
    print("\nCheck memory/plans/ directory for generated plan files.")
    print()


if __name__ == "__main__":
    main()
