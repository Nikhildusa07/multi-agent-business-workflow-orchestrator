from typing import Any

from sqlalchemy.orm import Session

from app.models.task import Task


def create_task(
    db: Session,
    workflow_id: int,
    task_name: str,
    assigned_agent: str,
) -> Task:
    task = Task(
        workflow_id=workflow_id,
        task_name=task_name,
        assigned_agent=assigned_agent,
        status="PENDING",
        retry_count=0,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def update_task(
    db: Session,
    task: Task,
    status: str,
    result: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> Task:
    task.status = status

    if result is not None:
        task.result = result

    if error_message is not None:
        task.error_message = error_message

    db.commit()
    db.refresh(task)

    return task