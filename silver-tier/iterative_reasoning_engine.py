"""
Iterative Reasoning Engine - Core Implementation
Executes tasks step-by-step with continuous plan updates and failure recovery.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class StepStatus(Enum):
    """Step execution status."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"


class PlanStatus(Enum):
    """Plan execution status."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    OBSOLETE = "OBSOLETE"


class RecoveryType(Enum):
    """Recovery strategy types."""
    RETRY = "RETRY"
    ALTERNATIVE = "ALTERNATIVE"
    SKIP_AND_CONTINUE = "SKIP_AND_CONTINUE"
    ABORT = "ABORT"
    CONTINUE = "CONTINUE"


@dataclass
class Step:
    """Represents a single execution step."""
    id: str
    name: str
    description: str
    actions: List[str]
    expected_outputs: List[str]
    status: StepStatus = StepStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 3
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_outputs: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    is_critical: bool = True
    risk_level: str = "MEDIUM"


@dataclass
class StepResult:
    """Result of step execution."""
    status: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    duration: Optional[float] = None
    message: str = ""
    retry_strategy: Optional[str] = None
    recovery_strategy: Optional[Dict] = None
    confidence: float = 1.0
    is_unexpected: bool = False
    invalidates_assumptions: bool = False
    suggests_better_approach: bool = False
    intervention_reason: Optional[str] = None


@dataclass
class Plan:
    """Represents an execution plan."""
    id: str
    objective: str
    success_criteria: List[str]
    context: Dict[str, Any]
    steps: List[Step]
    status: PlanStatus = PlanStatus.NOT_STARTED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    notes: str = ""
    completion_summary: Optional[Dict] = None


# ============================================================================
# ITERATIVE REASONING ENGINE
# ============================================================================

class IterativeReasoningEngine:
    """
    Core engine for iterative task execution with plan updates.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plans_dir = Path(config.get('plans_dir', 'memory/plans'))
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.current_plan: Optional[Plan] = None
        self.execution_log: List[Dict] = []

    # ------------------------------------------------------------------------
    # PLAN CREATION
    # ------------------------------------------------------------------------

    def analyze_and_create_plan(self, task: Dict[str, Any]) -> Plan:
        """
        Analyze a task and generate an execution plan.

        Args:
            task: Task dictionary with description, context, requirements

        Returns:
            Plan object ready for execution
        """
        # Extract objective
        objective = task.get('objective', task.get('description', 'Unknown objective'))

        # Define success criteria
        success_criteria = task.get('success_criteria', [
            'Task completed without errors',
            'All outputs generated',
            'Quality checks passed'
        ])

        # Gather context
        context = {
            'source': task.get('source', 'unknown'),
            'priority': task.get('priority', 'MEDIUM'),
            'deadline': task.get('deadline'),
            'resources': task.get('resources', []),
            'constraints': task.get('constraints', []),
            'assumptions': task.get('assumptions', [])
        }

        # Decompose into steps
        steps = self._decompose_into_steps(objective, context, task)

        # Create plan
        plan = Plan(
            id=self._generate_plan_id(),
            objective=objective,
            success_criteria=success_criteria,
            context=context,
            steps=steps
        )

        # Write initial plan
        self._write_plan_markdown(plan)

        self._log_event('PLAN_CREATED', plan.id, f'Created plan with {len(steps)} steps')

        return plan

    def _decompose_into_steps(self, objective: str, context: Dict, task: Dict) -> List[Step]:
        """
        Break down objective into executable steps.
        """
        # Check if steps are provided in task
        if 'steps' in task:
            return [
                Step(
                    id=f"step-{i+1:03d}",
                    name=s.get('name', f'Step {i+1}'),
                    description=s.get('description', ''),
                    actions=s.get('actions', []),
                    expected_outputs=s.get('expected_outputs', []),
                    dependencies=s.get('dependencies', []),
                    is_critical=s.get('is_critical', True)
                )
                for i, s in enumerate(task['steps'])
            ]

        # Auto-generate steps based on task type
        task_type = self._classify_task_type(objective)

        if task_type == 'DATA_PROCESSING':
            return self._create_data_processing_steps()
        elif task_type == 'REPORT_GENERATION':
            return self._create_report_generation_steps()
        elif task_type == 'INTEGRATION':
            return self._create_integration_steps()
        else:
            return self._create_generic_steps(objective)

    def _classify_task_type(self, objective: str) -> str:
        """Classify task type based on objective."""
        objective_lower = objective.lower()

        if any(kw in objective_lower for kw in ['data', 'analyze', 'process', 'calculate']):
            return 'DATA_PROCESSING'
        elif any(kw in objective_lower for kw in ['report', 'generate', 'document', 'summary']):
            return 'REPORT_GENERATION'
        elif any(kw in objective_lower for kw in ['integrate', 'connect', 'api', 'sync']):
            return 'INTEGRATION'
        else:
            return 'GENERIC'

    def _create_data_processing_steps(self) -> List[Step]:
        """Create steps for data processing tasks."""
        return [
            Step(
                id="step-001",
                name="Fetch Data",
                description="Retrieve data from sources",
                actions=["connect_to_source", "execute_query", "export_data"],
                expected_outputs=["raw_data_file"]
            ),
            Step(
                id="step-002",
                name="Validate and Clean Data",
                description="Check data quality and clean",
                actions=["validate_schema", "check_nulls", "remove_duplicates", "standardize_formats"],
                expected_outputs=["clean_data_file", "quality_report"],
                dependencies=["step-001"]
            ),
            Step(
                id="step-003",
                name="Process Data",
                description="Apply transformations and calculations",
                actions=["transform_data", "calculate_metrics", "aggregate_results"],
                expected_outputs=["processed_data_file"],
                dependencies=["step-002"]
            ),
            Step(
                id="step-004",
                name="Generate Outputs",
                description="Create final output artifacts",
                actions=["format_results", "create_visualizations", "export_outputs"],
                expected_outputs=["final_output"],
                dependencies=["step-003"]
            )
        ]

    def _create_report_generation_steps(self) -> List[Step]:
        """Create steps for report generation tasks."""
        return [
            Step(
                id="step-001",
                name="Gather Information",
                description="Collect all required information",
                actions=["identify_sources", "collect_data", "verify_completeness"],
                expected_outputs=["source_data"]
            ),
            Step(
                id="step-002",
                name="Analyze and Synthesize",
                description="Analyze data and generate insights",
                actions=["analyze_data", "identify_trends", "generate_insights"],
                expected_outputs=["analysis_results"],
                dependencies=["step-001"]
            ),
            Step(
                id="step-003",
                name="Create Report",
                description="Generate formatted report document",
                actions=["load_template", "populate_content", "add_visualizations", "format_document"],
                expected_outputs=["report_draft"],
                dependencies=["step-002"]
            ),
            Step(
                id="step-004",
                name="Review and Finalize",
                description="Quality check and finalize report",
                actions=["quality_check", "spell_check", "verify_accuracy", "export_final"],
                expected_outputs=["final_report"],
                dependencies=["step-003"]
            )
        ]

    def _create_generic_steps(self, objective: str) -> List[Step]:
        """Create generic steps for unknown task types."""
        return [
            Step(
                id="step-001",
                name="Prepare",
                description="Gather inputs and validate prerequisites",
                actions=["validate_inputs", "check_resources", "setup_environment"],
                expected_outputs=["preparation_complete"]
            ),
            Step(
                id="step-002",
                name="Execute",
                description="Perform main task actions",
                actions=["execute_main_task"],
                expected_outputs=["task_output"],
                dependencies=["step-001"]
            ),
            Step(
                id="step-003",
                name="Verify",
                description="Validate results and check success criteria",
                actions=["validate_outputs", "check_success_criteria"],
                expected_outputs=["verification_report"],
                dependencies=["step-002"]
            )
        ]

    # ------------------------------------------------------------------------
    # PLAN EXECUTION
    # ------------------------------------------------------------------------

    def execute_plan_iteratively(self, plan: Plan) -> Plan:
        """
        Execute plan one step at a time with continuous re-evaluation.

        Args:
            plan: Plan to execute

        Returns:
            Completed plan with results
        """
        self.current_plan = plan
        plan.status = PlanStatus.IN_PROGRESS
        self._write_plan_markdown(plan)

        iteration = 0
        max_iterations = len(plan.steps) * plan.steps[0].max_attempts

        while not self._is_plan_complete(plan) and iteration < max_iterations:
            iteration += 1

            # Re-evaluate plan state
            self._evaluate_plan_state(plan)

            # Get next executable step
            next_step = self._get_next_step(plan)

            if next_step is None:
                # No executable steps
                if self._has_blocked_steps(plan):
                    self._handle_blocked_plan(plan)
                break

            # Execute the step
            result = self._execute_step(plan, next_step)

            # Update plan based on result
            self._update_plan_after_step(plan, next_step, result)

            # Check if replanning needed
            if self._should_replan(plan, result):
                self._replan(plan, result)

            # Check if human intervention needed
            if self._requires_human_intervention(plan, result):
                self._request_human_intervention(plan, next_step, result)
                break

        # Finalize plan
        self._finalize_plan(plan)

        return plan

    def _get_next_step(self, plan: Plan) -> Optional[Step]:
        """Get the next executable step."""
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue

            if not self._are_dependencies_met(step, plan):
                continue

            if step.attempts >= step.max_attempts:
                step.status = StepStatus.FAILED
                continue

            return step

        return None

    def _execute_step(self, plan: Plan, step: Step) -> StepResult:
        """Execute a single step."""
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now()
        step.attempts += 1
        self._write_plan_markdown(plan)

        self._log_event('STEP_STARTED', plan.id, f'Starting {step.id}: {step.name}')

        try:
            # Execute step actions
            outputs = {}
            for action in step.actions:
                action_result = self._execute_action(action, step, plan)
                outputs[action] = action_result

            # Validate outputs
            if self._validate_step_outputs(step, outputs):
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now()
                step.actual_outputs = outputs

                duration = (step.completed_at - step.started_at).total_seconds()

                result = StepResult(
                    status='SUCCESS',
                    outputs=outputs,
                    duration=duration,
                    message='Step completed successfully'
                )

                self._log_event('STEP_COMPLETED', plan.id, f'Completed {step.id}')
            else:
                raise ValueError("Output validation failed")

        except Exception as error:
            result = self._handle_step_failure(plan, step, error)

        self._write_plan_markdown(plan)
        return result

    def _execute_action(self, action: str, step: Step, plan: Plan) -> Any:
        """
        Execute a single action within a step.
        This is where actual work happens - override in subclasses.
        """
        # Simulate action execution
        time.sleep(0.1)  # Simulate work

        # Return simulated result
        return {
            'action': action,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }

    def _validate_step_outputs(self, step: Step, outputs: Dict) -> bool:
        """Validate that step outputs meet expectations."""
        # Simple validation: check that we have outputs
        return len(outputs) > 0

    def _handle_step_failure(self, plan: Plan, step: Step, error: Exception) -> StepResult:
        """Handle step failure with retry logic."""
        self._log_event('STEP_FAILED', plan.id, f'Step {step.id} failed: {error}')

        can_retry = step.attempts < step.max_attempts

        if can_retry:
            step.status = StepStatus.PENDING
            step.notes += f'\nAttempt {step.attempts} failed: {error}. Will retry...'

            return StepResult(
                status='RETRY',
                error=error,
                retry_strategy='IMMEDIATE',
                message=f'Step failed, will retry ({step.attempts}/{step.max_attempts})'
            )
        else:
            step.status = StepStatus.FAILED
            step.notes += f'\nStep failed after {step.attempts} attempts: {error}'

            return StepResult(
                status='FAILED',
                error=error,
                message=f'Step failed after {step.attempts} attempts'
            )

    # ------------------------------------------------------------------------
    # PLAN EVALUATION
    # ------------------------------------------------------------------------

    def _evaluate_plan_state(self, plan: Plan):
        """Re-evaluate plan state before each step."""
        plan.updated_at = datetime.now()

    def _should_replan(self, plan: Plan, result: StepResult) -> bool:
        """Determine if replanning is needed."""
        failed_count = sum(1 for s in plan.steps if s.status == StepStatus.FAILED)
        return failed_count >= 2 or result.suggests_better_approach

    def _replan(self, plan: Plan, result: StepResult):
        """Regenerate plan based on current state."""
        self._log_event('REPLANNING', plan.id, 'Regenerating plan')
        # Simplified: just mark for human review
        plan.status = PlanStatus.AWAITING_APPROVAL

    def _requires_human_intervention(self, plan: Plan, result: StepResult) -> bool:
        """Check if human intervention is needed."""
        return result.status == 'FAILED' and result.confidence < 0.7

    def _request_human_intervention(self, plan: Plan, step: Step, result: StepResult):
        """Request human review."""
        plan.status = PlanStatus.AWAITING_APPROVAL
        self._log_event('INTERVENTION_REQUESTED', plan.id, 'Human review requested')

    # ------------------------------------------------------------------------
    # PLAN COMPLETION
    # ------------------------------------------------------------------------

    def _is_plan_complete(self, plan: Plan) -> bool:
        """Check if plan execution is complete."""
        terminal_statuses = {StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED}
        return all(step.status in terminal_statuses for step in plan.steps)

    def _finalize_plan(self, plan: Plan):
        """Finalize plan and generate summary."""
        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        total = len(plan.steps)

        if completed == total:
            plan.status = PlanStatus.COMPLETED
        elif completed >= total * 0.8:
            plan.status = PlanStatus.COMPLETED  # Partial success
        else:
            plan.status = PlanStatus.FAILED

        plan.completed_at = datetime.now()
        duration = (plan.completed_at - plan.created_at).total_seconds()

        plan.completion_summary = {
            'status': plan.status.value,
            'completed_steps': f'{completed}/{total}',
            'total_time': f'{duration:.1f}s',
            'success_rate': f'{completed/total*100:.1f}%'
        }

        self._write_plan_markdown(plan)
        self._log_event('PLAN_COMPLETED', plan.id, f'Plan {plan.status.value}')

    # ------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------

    def _are_dependencies_met(self, step: Step, plan: Plan) -> bool:
        """Check if step dependencies are satisfied."""
        for dep_id in step.dependencies:
            dep_step = next((s for s in plan.steps if s.id == dep_id), None)
            if dep_step is None or dep_step.status != StepStatus.COMPLETED:
                return False
        return True

    def _has_blocked_steps(self, plan: Plan) -> bool:
        """Check if plan has blocked steps."""
        return any(s.status == StepStatus.BLOCKED for s in plan.steps)

    def _handle_blocked_plan(self, plan: Plan):
        """Handle a blocked plan."""
        plan.status = PlanStatus.BLOCKED
        self._log_event('PLAN_BLOCKED', plan.id, 'Plan execution blocked')

    def _update_plan_after_step(self, plan: Plan, step: Step, result: StepResult):
        """Update plan state after step execution."""
        plan.updated_at = datetime.now()
        self._write_plan_markdown(plan)

    def _generate_plan_id(self) -> str:
        """Generate unique plan ID."""
        return f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _log_event(self, event_type: str, plan_id: str, message: str):
        """Log an event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'plan_id': plan_id,
            'message': message
        }
        self.execution_log.append(event)
        print(f"[{event_type}] {message}")

    def _write_plan_markdown(self, plan: Plan):
        """Write plan to markdown file."""
        content = self._generate_plan_markdown(plan)
        plan_file = self.plans_dir / f'{plan.id}.md'
        plan_file.write_text(content, encoding='utf-8')

    def _generate_plan_markdown(self, plan: Plan) -> str:
        """Generate markdown content from plan."""
        lines = [
            f"# Execution Plan: {plan.objective}",
            "",
            f"**Plan ID:** {plan.id}",
            f"**Created:** {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Last Updated:** {plan.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Status:** {plan.status.value}",
            "",
            "---",
            "",
            "## Objective",
            "",
            plan.objective,
            "",
            "### Success Criteria",
        ]

        for criterion in plan.success_criteria:
            lines.append(f"- [ ] {criterion}")

        lines.extend([
            "",
            "---",
            "",
            "## Execution Steps",
            ""
        ])

        for step in plan.steps:
            lines.extend([
                f"### Step: {step.name}",
                f"**ID:** {step.id}",
                f"**Status:** {step.status.value}",
                f"**Attempts:** {step.attempts}/{step.max_attempts}",
                "",
                f"**Description:** {step.description}",
                "",
                f"**Actions:**"
            ])

            for action in step.actions:
                lines.append(f"- {action}")

            if step.notes:
                lines.extend(["", f"**Notes:** {step.notes}"])

            lines.extend(["", "---", ""])

        # Current state
        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        lines.extend([
            "## Current State",
            "",
            f"**Progress:** {completed}/{len(plan.steps)} steps completed",
            f"**Completion:** {completed/len(plan.steps)*100:.0f}%",
            ""
        ])

        if plan.completion_summary:
            lines.extend([
                "## Completion Summary",
                "",
                f"**Status:** {plan.completion_summary['status']}",
                f"**Completed Steps:** {plan.completion_summary['completed_steps']}",
                f"**Total Time:** {plan.completion_summary['total_time']}",
                ""
            ])

        return "\n".join(lines)
