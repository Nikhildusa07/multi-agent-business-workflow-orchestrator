from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.services.redis_service import (
    set_workflow_state,
    set_workflow_status,
)


def update_workflow_state(
    db: Session,
    workflow_id: int,
    status: str,
    current_state: str,
    error_message: str | None = None,
) -> Workflow:

    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id)
        .first()
    )

    if workflow is None:
        raise ValueError("Workflow not found")

    workflow.status = status
    workflow.current_state = current_state
    workflow.error_message = error_message

    db.commit()
    db.refresh(workflow)

    # Redis state
    set_workflow_state(
        workflow_id,
        {
            "workflow_id": workflow_id,
            "status": status,
            "current_state": current_state,
            "error_message": error_message,
        },
    )

    set_workflow_status(
        workflow_id,
        status,
    )

    return workflow