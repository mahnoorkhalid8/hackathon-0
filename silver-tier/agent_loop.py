"""
Agent Loop - Iterative Reasoning Engine
Executes tasks step-by-step with continuous plan updates and failure recovery.
"""

# ============================================================================
# AGENT LOOP PSEUDOCODE
# ============================================================================

# ----------------------------------------------------------------------------
# MAIN AGENT LOOP
# ----------------------------------------------------------------------------

function agent_loop():
    """
    Main iterative reasoning loop for Digital FTE.
    Continuously monitors for new tasks and executes them step-by-step.
    """

    initialize_agent()

    while agent_is_running:
        # Check for new tasks
        new_task = check_for_new_task()

        if new_task:
            # Generate execution plan
            plan = analyze_and_create_plan(new_task)

            # Execute plan iteratively
            execute_plan_iteratively(plan)

        sleep(polling_interval)


# ----------------------------------------------------------------------------
# TASK ANALYSIS AND PLAN GENERATION
# ----------------------------------------------------------------------------

function analyze_and_create_plan(task):
    """
    Analyze a new task and generate a detailed execution plan.

    Args:
        task: Task object with description, context, requirements

    Returns:
        plan: Plan object with steps, dependencies, success criteria
    """

    # Step 1: Understand the objective
    objective = extract_objective(task)
    success_criteria = define_success_criteria(task, objective)

    # Step 2: Gather context
    context = {
        'source': task.source,
        'priority': task.priority,
        'deadline': task.deadline,
        'resources': identify_available_resources(task),
        'constraints': identify_constraints(task),
        'assumptions': make_reasonable_assumptions(task)
    }

    # Step 3: Break down into steps
    steps = decompose_into_steps(objective, context)

    # Step 4: Identify dependencies
    steps = add_dependencies(steps)

    # Step 5: Create plan object
    plan = Plan(
        id=generate_plan_id(),
        objective=objective,
        success_criteria=success_criteria,
        context=context,
        steps=steps,
        status='NOT_STARTED',
        created_at=now(),
        updated_at=now()
    )

    # Step 6: Write initial Plan.md
    write_plan_to_markdown(plan, 'memory/plans/plan-{plan.id}.md')

    # Step 7: Log plan creation
    log_event('PLAN_CREATED', plan.id, f'Created plan with {len(steps)} steps')

    return plan


function decompose_into_steps(objective, context):
    """
    Break down objective into executable steps.
    Uses reasoning to determine optimal decomposition.
    """

    steps = []

    # Analyze objective complexity
    complexity = assess_complexity(objective)

    if complexity == 'SIMPLE':
        # Single step execution
        steps.append(create_step(
            name='Execute Task',
            description=objective,
            actions=extract_actions(objective)
        ))

    elif complexity == 'MODERATE':
        # Standard decomposition: prepare → execute → verify
        steps.append(create_step(
            name='Prepare',
            description='Gather inputs and validate prerequisites',
            actions=['validate_inputs', 'check_resources', 'setup_environment']
        ))

        steps.append(create_step(
            name='Execute',
            description='Perform main task actions',
            actions=extract_actions(objective)
        ))

        steps.append(create_step(
            name='Verify',
            description='Validate results and check success criteria',
            actions=['validate_outputs', 'check_success_criteria']
        ))

    elif complexity == 'COMPLEX':
        # Detailed decomposition based on task type
        if is_data_task(objective):
            steps = decompose_data_task(objective, context)
        elif is_report_task(objective):
            steps = decompose_report_task(objective, context)
        elif is_integration_task(objective):
            steps = decompose_integration_task(objective, context)
        else:
            steps = decompose_generic_task(objective, context)

    # Add step IDs and metadata
    for i, step in enumerate(steps):
        step.id = f'step-{i+1:03d}'
        step.status = 'PENDING'
        step.attempts = 0
        step.max_attempts = 3
        step.dependencies = []

    return steps


function decompose_data_task(objective, context):
    """Decompose data processing tasks."""
    return [
        create_step('Fetch Data', 'Retrieve data from sources', [...]),
        create_step('Validate Data', 'Check data quality and integrity', [...]),
        create_step('Transform Data', 'Apply transformations and calculations', [...]),
        create_step('Analyze Data', 'Perform analysis and generate insights', [...]),
        create_step('Generate Output', 'Create final output artifacts', [...]),
        create_step('Quality Check', 'Verify output meets requirements', [...])
    ]


# ----------------------------------------------------------------------------
# ITERATIVE PLAN EXECUTION
# ----------------------------------------------------------------------------

function execute_plan_iteratively(plan):
    """
    Execute plan one step at a time with continuous re-evaluation.

    Args:
        plan: Plan object with steps to execute
    """

    plan.status = 'IN_PROGRESS'
    update_plan_markdown(plan)

    while not is_plan_complete(plan):
        # Re-evaluate plan state
        evaluate_plan_state(plan)

        # Get next executable step
        next_step = get_next_step(plan)

        if next_step is None:
            # No executable steps (all blocked or complete)
            if has_blocked_steps(plan):
                handle_blocked_plan(plan)
            break

        # Execute the step
        result = execute_step(plan, next_step)

        # Update plan based on result
        update_plan_after_step(plan, next_step, result)

        # Re-evaluate if plan needs adjustment
        if should_replan(plan, result):
            replan(plan, result)

        # Check if human intervention needed
        if requires_human_intervention(plan, result):
            request_human_intervention(plan, next_step, result)
            break

    # Finalize plan
    finalize_plan(plan)


function get_next_step(plan):
    """
    Determine the next step to execute based on dependencies and status.

    Returns:
        step: Next executable step, or None if no steps available
    """

    for step in plan.steps:
        # Skip if not pending
        if step.status != 'PENDING':
            continue

        # Check if dependencies are met
        if not are_dependencies_met(step, plan):
            continue

        # Check if max attempts exceeded
        if step.attempts >= step.max_attempts:
            step.status = 'FAILED'
            continue

        # This step is ready to execute
        return step

    return None


function execute_step(plan, step):
    """
    Execute a single step with error handling and retry logic.

    Args:
        plan: Current plan
        step: Step to execute

    Returns:
        result: Execution result with status, outputs, errors
    """

    # Update step status
    step.status = 'IN_PROGRESS'
    step.started_at = now()
    step.attempts += 1
    update_plan_markdown(plan)

    log_event('STEP_STARTED', plan.id, f'Starting {step.id}: {step.name}')

    try:
        # Execute step actions
        outputs = {}

        for action in step.actions:
            action_result = execute_action(action, step, plan)
            outputs[action] = action_result

        # Validate outputs
        validation = validate_step_outputs(step, outputs)

        if validation.success:
            # Step succeeded
            step.status = 'COMPLETED'
            step.completed_at = now()
            step.actual_outputs = outputs

            result = StepResult(
                status='SUCCESS',
                outputs=outputs,
                duration=step.completed_at - step.started_at,
                message='Step completed successfully'
            )

            log_event('STEP_COMPLETED', plan.id, f'Completed {step.id}')

        else:
            # Validation failed
            raise ValidationError(validation.errors)

    except Exception as error:
        # Step failed
        result = handle_step_failure(plan, step, error)

    # Update plan
    update_plan_markdown(plan)

    return result


function handle_step_failure(plan, step, error):
    """
    Handle step failure with retry and recovery logic.

    Args:
        plan: Current plan
        step: Failed step
        error: Error that occurred

    Returns:
        result: Failure result with recovery strategy
    """

    log_event('STEP_FAILED', plan.id, f'Step {step.id} failed: {error}')

    # Determine if retry is possible
    can_retry = step.attempts < step.max_attempts

    if can_retry:
        # Determine retry strategy
        retry_strategy = determine_retry_strategy(step, error)

        if retry_strategy == 'IMMEDIATE':
            # Retry immediately with same parameters
            step.status = 'PENDING'
            step.notes += f'\nAttempt {step.attempts} failed: {error}. Retrying...'

        elif retry_strategy == 'WITH_MODIFICATION':
            # Retry with modified parameters
            step.status = 'PENDING'
            modify_step_for_retry(step, error)
            step.notes += f'\nAttempt {step.attempts} failed: {error}. Retrying with modifications...'

        elif retry_strategy == 'SKIP':
            # Skip this step and continue
            step.status = 'SKIPPED'
            step.notes += f'\nStep skipped after {step.attempts} attempts: {error}'

        result = StepResult(
            status='RETRY',
            error=error,
            retry_strategy=retry_strategy,
            message=f'Step failed, will retry ({step.attempts}/{step.max_attempts})'
        )

    else:
        # Max attempts reached
        step.status = 'FAILED'
        step.notes += f'\nStep failed after {step.attempts} attempts: {error}'

        # Determine recovery strategy
        recovery = determine_recovery_strategy(plan, step, error)

        result = StepResult(
            status='FAILED',
            error=error,
            recovery_strategy=recovery,
            message=f'Step failed after {step.attempts} attempts'
        )

    update_plan_markdown(plan)

    return result


function determine_recovery_strategy(plan, failed_step, error):
    """
    Determine how to recover from a failed step.

    Returns:
        strategy: Recovery strategy object
    """

    # Analyze failure impact
    impact = assess_failure_impact(plan, failed_step)

    if impact == 'CRITICAL':
        # Cannot continue without this step
        return RecoveryStrategy(
            type='ABORT',
            reason='Critical step failed, cannot continue',
            action='Request human intervention'
        )

    elif impact == 'HIGH':
        # Try alternative approach
        alternative = find_alternative_approach(plan, failed_step)

        if alternative:
            return RecoveryStrategy(
                type='ALTERNATIVE',
                reason='Primary approach failed, trying alternative',
                action=f'Execute alternative: {alternative.name}',
                alternative_step=alternative
            )
        else:
            return RecoveryStrategy(
                type='ABORT',
                reason='No alternative approach available',
                action='Request human intervention'
            )

    elif impact == 'MEDIUM':
        # Skip and continue with degraded functionality
        return RecoveryStrategy(
            type='SKIP_AND_CONTINUE',
            reason='Step failed but not critical',
            action='Continue with remaining steps',
            degradation='Some functionality may be limited'
        )

    else:  # LOW impact
        # Continue normally
        return RecoveryStrategy(
            type='CONTINUE',
            reason='Non-critical step failed',
            action='Continue with remaining steps'
        )


# ----------------------------------------------------------------------------
# PLAN RE-EVALUATION
# ----------------------------------------------------------------------------

function evaluate_plan_state(plan):
    """
    Re-evaluate plan state and adjust if needed.
    This is called before each step execution.
    """

    # Check if objective is still valid
    if not is_objective_still_valid(plan):
        plan.status = 'OBSOLETE'
        log_event('PLAN_OBSOLETE', plan.id, 'Objective no longer valid')
        return

    # Check if deadline is approaching
    if is_deadline_approaching(plan):
        # Prioritize critical steps
        reprioritize_steps(plan)
        log_event('PLAN_REPRIORITIZED', plan.id, 'Deadline approaching, reprioritized steps')

    # Check if resources are still available
    if not are_resources_available(plan):
        # Adjust plan for resource constraints
        adjust_for_resource_constraints(plan)
        log_event('PLAN_ADJUSTED', plan.id, 'Adjusted for resource constraints')

    # Update progress metrics
    update_progress_metrics(plan)


function should_replan(plan, last_result):
    """
    Determine if plan needs to be regenerated based on execution results.

    Returns:
        bool: True if replanning is needed
    """

    # Replan if multiple steps have failed
    if count_failed_steps(plan) >= 2:
        return True

    # Replan if execution is taking much longer than expected
    if is_significantly_delayed(plan):
        return True

    # Replan if new information invalidates assumptions
    if last_result.invalidates_assumptions:
        return True

    # Replan if better approach discovered
    if last_result.suggests_better_approach:
        return True

    return False


function replan(plan, trigger_result):
    """
    Regenerate plan based on current state and new information.
    """

    log_event('REPLANNING', plan.id, f'Regenerating plan due to: {trigger_result.reason}')

    # Preserve completed steps
    completed_steps = [s for s in plan.steps if s.status == 'COMPLETED']

    # Analyze what remains to be done
    remaining_objective = determine_remaining_objective(plan, completed_steps)

    # Generate new steps for remaining work
    new_steps = decompose_into_steps(remaining_objective, plan.context)

    # Merge completed and new steps
    plan.steps = completed_steps + new_steps

    # Update plan metadata
    plan.updated_at = now()
    plan.notes += f'\n\nPlan regenerated at {now()}: {trigger_result.reason}'

    # Write updated plan
    update_plan_markdown(plan)

    log_event('REPLANNED', plan.id, f'Plan regenerated with {len(new_steps)} new steps')


# ----------------------------------------------------------------------------
# PLAN COMPLETION
# ----------------------------------------------------------------------------

function is_plan_complete(plan):
    """
    Check if plan execution is complete.

    Returns:
        bool: True if plan is complete (success or failure)
    """

    # Check if all steps are in terminal state
    all_terminal = all(
        step.status in ['COMPLETED', 'FAILED', 'SKIPPED']
        for step in plan.steps
    )

    if not all_terminal:
        return False

    # Check success criteria
    success_criteria_met = check_success_criteria(plan)

    if success_criteria_met:
        plan.status = 'COMPLETED'
        return True

    # Check if any critical steps failed
    has_critical_failures = any(
        step.status == 'FAILED' and step.is_critical
        for step in plan.steps
    )

    if has_critical_failures:
        plan.status = 'FAILED'
        return True

    # Partial completion
    completed_count = count_completed_steps(plan)
    total_count = len(plan.steps)

    if completed_count >= total_count * 0.8:  # 80% threshold
        plan.status = 'COMPLETED'  # Partial success
        return True
    else:
        plan.status = 'FAILED'  # Insufficient completion
        return True


function finalize_plan(plan):
    """
    Finalize plan execution and generate completion summary.
    """

    # Calculate final metrics
    completed_steps = count_completed_steps(plan)
    total_steps = len(plan.steps)
    success_criteria_met = count_success_criteria_met(plan)
    total_criteria = len(plan.success_criteria)
    total_time = now() - plan.created_at

    # Generate completion summary
    summary = CompletionSummary(
        status=plan.status,
        completed_steps=f'{completed_steps}/{total_steps}',
        success_criteria_met=f'{success_criteria_met}/{total_criteria}',
        total_time=format_duration(total_time),
        final_outputs=collect_final_outputs(plan),
        lessons_learned=extract_lessons_learned(plan),
        recommendations=generate_recommendations(plan)
    )

    # Update plan with summary
    plan.completion_summary = summary
    plan.completed_at = now()

    # Write final plan
    update_plan_markdown(plan)

    # Move to appropriate archive
    if plan.status == 'COMPLETED':
        archive_path = 'memory/Done/'
    else:
        archive_path = 'memory/Failed/'

    move_plan_to_archive(plan, archive_path)

    # Update dashboard
    update_dashboard_with_completion(plan)

    # Log completion
    log_event('PLAN_COMPLETED', plan.id, f'Plan {plan.status}: {summary}')

    # Notify stakeholders if needed
    if plan.priority == 'HIGH' or plan.status == 'FAILED':
        notify_stakeholders(plan, summary)


# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

function update_plan_markdown(plan):
    """
    Update Plan.md file with current plan state.
    This is called after every significant change.
    """

    plan.updated_at = now()

    markdown_content = generate_plan_markdown(plan)

    plan_file = f'memory/plans/plan-{plan.id}.md'
    write_file(plan_file, markdown_content)

    # Also update a symlink to "current plan" for easy access
    if plan.status == 'IN_PROGRESS':
        create_symlink('memory/Plan.md', plan_file)


function generate_plan_markdown(plan):
    """
    Generate markdown content from plan object.
    Uses the template structure.
    """

    # Load template
    template = load_template('templates/plan-template.md')

    # Fill in plan details
    content = template.replace('[TASK_NAME]', plan.objective)
    content = content.replace('[PLAN_ID]', plan.id)
    content = content.replace('[TIMESTAMP]', plan.updated_at)
    content = content.replace('[STATUS]', plan.status)

    # Add steps section
    steps_section = generate_steps_section(plan.steps)
    content = content.replace('[STEPS_SECTION]', steps_section)

    # Add current state
    current_state = generate_current_state_section(plan)
    content = content.replace('[CURRENT_STATE]', current_state)

    # Add execution log
    execution_log = generate_execution_log(plan)
    content = content.replace('[EXECUTION_LOG]', execution_log)

    return content


function requires_human_intervention(plan, result):
    """
    Determine if human intervention is needed.

    Returns:
        bool: True if human should review before continuing
    """

    # Critical failure
    if result.status == 'FAILED' and result.is_critical:
        return True

    # Ambiguous situation
    if result.confidence < 0.7:
        return True

    # Unexpected result
    if result.is_unexpected:
        return True

    # High-risk next step
    next_step = get_next_step(plan)
    if next_step and next_step.risk_level == 'HIGH':
        return True

    return False


function request_human_intervention(plan, step, result):
    """
    Request human review and approval before continuing.
    """

    # Create intervention request
    request = InterventionRequest(
        plan_id=plan.id,
        step_id=step.id,
        reason=result.intervention_reason,
        context=result.context,
        options=result.suggested_options,
        urgency=determine_urgency(plan, result)
    )

    # Move to approval queue
    approval_file = f'memory/Needs_Approval/plan-{plan.id}-intervention.md'
    write_intervention_request(approval_file, request)

    # Update plan status
    plan.status = 'AWAITING_APPROVAL'
    update_plan_markdown(plan)

    # Update dashboard
    update_dashboard_with_intervention_request(plan, request)

    log_event('INTERVENTION_REQUESTED', plan.id, f'Human review requested: {request.reason}')


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Initialize and start agent loop
    agent_loop()
