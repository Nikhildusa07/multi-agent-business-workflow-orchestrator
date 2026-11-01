from unittest.mock import patch

from app.database.session import SessionLocal
from app.models.task import Task
from app.models.workflow import Workflow
from app.services.execution_service import (
    execute_task_with_retry,
)


def test_task_retry_stops_after_three_attempts():
    db = SessionLocal()

    try:
        workflow = Workflow(
            workflow_name="Retry Limit Test",
            input_data={
                "request": "Test retry failure",
                "priority": "high",
            },
            status="RUNNING",
            current_state="EXECUTION",
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        task_data = {
            "task_name": "Intentional Failure Test",
            "assigned_agent": "execution_agent",
            "action": "invalid_action_for_test",
        }

        with patch(
            "app.services.execution_service.execution_agent"
        ) as mock_agent:

            mock_agent.return_value = {
                "success": False,
                "message": "Intentional test failure",
            }

            result = execute_task_with_retry(
                db=db,
                workflow_id=workflow.id,
                task_data=task_data,
            )

            assert result["success"] is False
            assert result["retry_count"] == 3

            assert mock_agent.call_count == 3

        task = (
            db.query(Task)
            .filter(
                Task.workflow_id == workflow.id
            )
            .first()
        )

        assert task is not None
        assert task.status == "FAILED"
        assert task.retry_count == 3

    finally:
        db.close()