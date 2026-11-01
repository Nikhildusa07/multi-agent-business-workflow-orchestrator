from typing import Final

from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.services.audit_service import create_audit_log


# Allowed workflow state transitions.
# Each key can transition only to the states listed in its value.
STATE_TRANSITIONS: Final[dict[str, set[str]]] = {
    "PENDING": {"INTAKE", "FAILED"},
    "INTAKE": {"PLANNING", "FAILED"},
    "PLANNING": {"EXECUTION", "FAILED"},
    "EXECUTION": {"EXECUTION", "REVIEW", "APPROVAL", "FAILED"},
    "APPROVAL": {"EXECUTION", "FAILED"},
    "REVIEW": {"COMPLETED", "FAILED"},
    "FAILED": {"INTAKE", "FAILED"},
    "COMPLETED": set(),
}


STATE_STATUS: Final[dict[str, str]] = {
    "PENDING": "PENDING",
    "INTAKE": "RUNNING",
    "PLANNING": "RUNNING",
    "EXECUTION": "RUNNING",
    "APPROVAL": "PENDING_APPROVAL",
    "REVIEW": "RUNNING",
    "COMPLETED": "COMPLETED",
    "FAILED": "FAILED",
}


class InvalidStateTransition(Exception):
    """Raised when a workflow attempts an invalid state transition."""


def validate_transition(
    current_state: str,
    next_state: str,
) -> bool:
    """
    Validate whether a workflow can move from current_state to next_state.
    """

    if current_state == next_state:
        return True

    allowed_states = STATE_TRANSITIONS.get(current_state, set())

    if next_state not in allowed_states:
        raise InvalidStateTransition(
            f"Invalid workflow transition: "
            f"{current_state} -> {next_state}"
        )

    return True


def transition_workflow(
    db: Session,
    workflow: Workflow,
    next_state: str,
    *,
    error_message: str | None = None,
    agent: str = "SYSTEM",
    action: str = "STATE_TRANSITION",
) -> Workflow:
    """
    Safely transition a workflow to the next state.

    This function:
    1. Validates the transition.
    2. Updates current_state.
    3. Updates workflow status.
    4. Stores any error message.
    5. Creates an audit log.
    """

    current_state = workflow.current_state

    validate_transition(
        current_state=current_state,
        next_state=next_state,
    )

    workflow.current_state = next_state
    workflow.status = STATE_STATUS.get(
        next_state,
        "FAILED",
    )
    workflow.error_message = error_message

    db.commit()
    db.refresh(workflow)

    create_audit_log(
        db=db,
        workflow_id=workflow.id,
        agent=agent,
        action=action,
        status=workflow.status,
        message=(
            f"Workflow state transition: "
            f"{current_state} -> {next_state}"
        ),
    )

    return workflow


def can_transition(
    current_state: str,
    next_state: str,
) -> bool:
    """
    Return True when a transition is valid, otherwise False.
    """

    try:
        validate_transition(
            current_state=current_state,
            next_state=next_state,
        )
        return True
    except InvalidStateTransition:
        return False