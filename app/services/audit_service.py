from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    workflow_id: int,
    agent: str,
    action: str,
    status: str,
    message: str | None = None,
    task_id: int | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        workflow_id=workflow_id,
        task_id=task_id,
        agent=agent,
        action=action,
        status=status,
        message=message,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log