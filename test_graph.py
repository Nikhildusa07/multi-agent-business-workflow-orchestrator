from app.database.session import SessionLocal
from app.models.workflow import Workflow
from app.orchestration.graph import build_workflow_graph
from app.orchestration.transitions import transition_workflow


def test_workflow_graph_execution():
    db = SessionLocal()

    try:
        workflow = Workflow(
            workflow_name="Graph State Transition Test",
            input_data={
                "request": "Create a business performance report",
                "priority": "high",
            },
            status="PENDING",
            current_state="PENDING",
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        transition_workflow(
            db=db,
            workflow=workflow,
            next_state="INTAKE",
            agent="TEST",
            action="TEST_WORKFLOW_STARTED",
        )

        workflow_graph = build_workflow_graph(db)

        initial_state = {
            "workflow_id": workflow.id,
            "workflow_input": workflow.input_data,
            "status": "RUNNING",
            "current_state": "INTAKE",
            "retry_count": 0,
            "max_retries": 3,
            "current_task_index": 0,
            "tasks": [],
            "execution_results": [],
            "review_results": [],
            "approval_granted": False,
            "approval_id": None,
            "error_message": None,
        }

        result = workflow_graph.invoke(initial_state)

        print("\n===== WORKFLOW RESULT =====")
        print("Workflow ID:", workflow.id)
        print("Status:", result.get("status"))
        print("Current State:", result.get("current_state"))

        print("\n===== INTAKE =====")
        print(result.get("intake_result"))

        print("\n===== PLAN =====")
        print(result.get("planning_result"))

        print("\n===== EXECUTION =====")
        for execution in result.get(
            "execution_results",
            [],
        ):
            print(execution)

        print("\n===== REVIEW =====")
        for review in result.get(
            "review_results",
            [],
        ):
            print(review)

        assert result.get("status") == "COMPLETED"
        assert result.get("current_state") == "COMPLETED"

        db.refresh(workflow)

        assert workflow.status == "COMPLETED"
        assert workflow.current_state == "COMPLETED"

    finally:
        db.close()