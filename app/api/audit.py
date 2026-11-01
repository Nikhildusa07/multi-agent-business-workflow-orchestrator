from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.audit import AuditLog

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "workflow_id": log.workflow_id,
            "task_id": log.task_id,
            "agent": log.agent,
            "action": log.action,
            "status": log.status,
            "message": log.message,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]