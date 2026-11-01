from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.services.audit_service import create_audit_log


def create_approval(
    db: Session,
    workflow_id: int,
    task_id: int | None,
    requested_by: str,
) -> Approval:
    approval = Approval(
        workflow_id=workflow_id,
        task_id=task_id,
        requested_by=requested_by,
        status="PENDING",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    create_audit_log(
        db=db,
        workflow_id=workflow_id,
        task_id=task_id,
        agent="approval_service",
        action="APPROVAL_REQUESTED",
        status="PENDING",
        message="Human approval requested for consequential action.",
    )

    return approval


def update_approval(
    db: Session,
    approval: Approval,
    status: str,
    approved_by: str,
) -> Approval:
    approval.status = status
    approval.approved_by = approved_by
    approval.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(approval)

    create_audit_log(
        db=db,
        workflow_id=approval.workflow_id,
        task_id=approval.task_id,
        agent="approval_service",
        action=f"APPROVAL_{status}",
        status=status,
        message=f"Approval {status.lower()} by {approved_by}.",
    )

    return approval