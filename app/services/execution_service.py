from typing import Any

from sqlalchemy.orm import Session

from app.agents.execution_agent import execution_agent
from app.models.task import Task
from app.services.audit_service import create_audit_log
from app.services.task_service import update_task


MAX_RETRIES = 3


def execute_task_with_retry(
    db: Session,
    workflow_id: int,
    task_data: dict[str, Any],
) -> dict[str, Any]:
    task = Task(
        workflow_id=workflow_id,
        task_name=task_data["task_name"],
        assigned_agent=task_data["assigned_agent"],
        status="RUNNING",
        retry_count=0,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        workflow_id=workflow_id,
        task_id=task.id,
        agent=task.assigned_agent,
        action="TASK_STARTED",
        status="RUNNING",
        message=f"Started task: {task.task_name}",
    )

    while task.retry_count < MAX_RETRIES:
        result = execution_agent(task_data)

        if result.get("success"):
            update_task(
                db=db,
                task=task,
                status="COMPLETED",
                result=result,
            )

            create_audit_log(
                db=db,
                workflow_id=workflow_id,
                task_id=task.id,
                agent=task.assigned_agent,
                action="TASK_COMPLETED",
                status="SUCCESS",
                message=result.get("message"),
            )

            return result

        task.retry_count += 1
        task.status = "RETRYING"
        task.error_message = result.get("message")

        db.commit()
        db.refresh(task)

        create_audit_log(
            db=db,
            workflow_id=workflow_id,
            task_id=task.id,
            agent=task.assigned_agent,
            action="TASK_RETRY",
            status="RETRYING",
            message=f"Retry {task.retry_count}/{MAX_RETRIES}",
        )

    task.status = "FAILED"
    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        workflow_id=workflow_id,
        task_id=task.id,
        agent=task.assigned_agent,
        action="TASK_FAILED",
        status="FAILED",
        message="Maximum retry limit reached.",
    )

    return {
        "success": False,
        "task_name": task.task_name,
        "message": "Task failed after maximum retries.",
        "retry_count": task.retry_count,
    }


def execute_workflow_tasks(
    db: Session,
    workflow_id: int,
    tasks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    execution_results = []

    for task_data in tasks:
        result = execute_task_with_retry(
            db=db,
            workflow_id=workflow_id,
            task_data=task_data,
        )

        execution_results.append(result)

        if not result.get("success"):
            break

    return execution_results