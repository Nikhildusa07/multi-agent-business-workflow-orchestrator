from app.database.session import SessionLocal
from app.models.workflow import Workflow
from app.services.execution_service import execute_workflow_tasks


db = SessionLocal()

try:
    workflow = Workflow(
        workflow_name="Persistence Test Workflow",
        input_data={
            "request": "Create a business performance report",
            "priority": "high",
        },
        status="EXECUTION",
        current_state="EXECUTION",
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    print(f"Workflow created: {workflow.id}")

    tasks = [
        {
            "task_name": "Collect business data",
            "assigned_agent": "execution_agent",
            "action": "collect_data",
        },
        {
            "task_name": "Analyze business performance",
            "assigned_agent": "execution_agent",
            "action": "analyze_data",
        },
        {
            "task_name": "Generate business report",
            "assigned_agent": "execution_agent",
            "action": "generate_report",
        },
    ]

    results = execute_workflow_tasks(
        db=db,
        workflow_id=workflow.id,
        tasks=tasks,
    )

    print("\nExecution results:")

    for result in results:
        print(result)

    workflow.status = "COMPLETED"
    workflow.current_state = "REVIEW"

    db.commit()

    print("\nWorkflow persistence test successful!")

finally:
    db.close()