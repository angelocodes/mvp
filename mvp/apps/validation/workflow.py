from .models import ValidationStep


def get_workflow_state(project):
    """Get current workflow state for a project"""
    steps = ValidationStep.objects.filter(project=project).order_by('created_at')
    current_step = project.status.lower()
    completed_steps = [step.step for step in steps if step.completed]
    locked_steps = []

    # Define workflow order
    workflow_order = ['linearity', 'accuracy', 'precision', 'lod_loq']

    # Find current step index
    try:
        current_index = workflow_order.index(current_step)
    except ValueError:
        current_index = 0

    # Locked steps are those after current if current not passed
    if current_step in workflow_order:
        step_obj = steps.filter(step=current_step).first()
        if step_obj and not step_obj.passed:
            locked_steps = workflow_order[current_index + 1:]

    allowed_actions = []
    if current_step == 'draft':
        allowed_actions = ['start_validation']
    elif current_step in workflow_order:
        if not steps.filter(step=current_step).exists():
            allowed_actions = [f'submit_{current_step}']
        else:
            step_obj = steps.get(step=current_step)
            if step_obj.completed:
                if step_obj.passed:
                    next_step = workflow_order[current_index + 1] if current_index + 1 < len(workflow_order) else None
                    if next_step:
                        allowed_actions = [f'submit_{next_step}']
                    else:
                        allowed_actions = ['review']
                else:
                    allowed_actions = []  # blocked
            else:
                allowed_actions = [f'update_{current_step}']  # but according to API, no updates

    return {
        'current_step': current_step,
        'completed_steps': completed_steps,
        'allowed_next_actions': allowed_actions,
        'locked_steps': locked_steps,
    }


def advance_workflow(project, step, passed):
    """Advance workflow after completing a step"""
    workflow_order = ['linearity', 'accuracy', 'precision', 'lod_loq']
    if step in workflow_order:
        index = workflow_order.index(step)
        if passed and index + 1 < len(workflow_order):
            project.status = workflow_order[index + 1].upper()
        elif passed:
            project.status = 'review'
        else:
            project.status = step.upper()  # stay, but blocked
        project.save()
