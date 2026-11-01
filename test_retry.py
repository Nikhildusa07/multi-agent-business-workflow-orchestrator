from app.database.session import SessionLocal
from app.services.execution_service import execute_task_with_retry


db = SessionLocal()

try:
    task = {
        "task_name": "Invalid Test Task",
        "assigned_agent": "execution_agent",
        "action": "invalid_action",
    }

    result = execute_task_with_retry(
        db=db,
        workflow_id=1,
        task_data=task,
    )

    print("\n===== RETRY TEST =====")
    print(result)

finally:
    db.close()