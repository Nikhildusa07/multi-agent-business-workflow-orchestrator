from typing import Any

from app.services.redis_service import (
    get_workflow_checkpoint,
)


def get_recovery_checkpoint(
    workflow_id: int,
) -> dict[str, Any] | None:
    """
    Return the latest Redis checkpoint for a workflow.
    """

    checkpoint = get_workflow_checkpoint(
        workflow_id
    )

    if checkpoint is None:
        return None

    return checkpoint


def can_recover_workflow(
    workflow_id: int,
) -> bool:
    """
    Check whether a workflow has a usable
    Redis checkpoint for recovery.
    """

    checkpoint = get_recovery_checkpoint(
        workflow_id
    )

    if checkpoint is None:
        return False

    current_state = checkpoint.get(
        "current_state"
    )

    status = checkpoint.get("status")

    return (
        status in {
            "RUNNING",
            "PENDING_APPROVAL",
        }
        and current_state in {
            "INTAKE",
            "PLANNING",
            "EXECUTION",
            "APPROVAL",
            "REVIEW",
        }
    )