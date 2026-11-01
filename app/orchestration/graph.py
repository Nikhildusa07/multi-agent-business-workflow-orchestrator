from typing import Any

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.intake_agent import intake_agent
from app.agents.planning_agent import planning_agent
from app.agents.review_agent import review_agent
from app.models.workflow import Workflow
from app.orchestration.state import WorkflowState
from app.orchestration.transitions import transition_workflow
from app.services.approval_service import create_approval
from app.services.audit_service import create_audit_log
from app.services.execution_service import execute_task_with_retry
from app.services.redis_service import (
    clear_workflow_checkpoint,
    save_workflow_checkpoint,
)


def build_workflow_graph(db: Session):
    def get_workflow(
        workflow_id: int,
    ) -> Workflow | None:
        return (
            db.query(Workflow)
            .filter(Workflow.id == workflow_id)
            .first()
        )

    def save_checkpoint(
        state: WorkflowState,
        *,
        status: str | None = None,
        current_state: str | None = None,
        current_task_index: int | None = None,
        retry_count: int | None = None,
        approval_id: int | None = None,
        error_message: str | None = None,
        tasks: list[dict[str, Any]] | None = None,
        execution_results: list[dict[str, Any]] | None = None,
        review_results: list[dict[str, Any]] | None = None,
    ) -> None:
        save_workflow_checkpoint(
            workflow_id=state["workflow_id"],
            status=status or state.get(
                "status",
                "RUNNING",
            ),
            current_state=current_state or state.get(
                "current_state",
                "PENDING",
            ),
            current_task_index=(
                current_task_index
                if current_task_index is not None
                else state.get(
                    "current_task_index",
                    0,
                )
            ),
            retry_count=(
                retry_count
                if retry_count is not None
                else state.get(
                    "retry_count",
                    0,
                )
            ),
            approval_id=(
                approval_id
                if approval_id is not None
                else state.get("approval_id")
            ),
            error_message=error_message,
            tasks=(
                tasks
                if tasks is not None
                else state.get("tasks", [])
            ),
            execution_results=(
                execution_results
                if execution_results is not None
                else state.get(
                    "execution_results",
                    [],
                )
            ),
            review_results=(
                review_results
                if review_results is not None
                else state.get(
                    "review_results",
                    [],
                )
            ),
            workflow_input=state.get(
                "workflow_input",
                {},
            ),
        )

    def fail_workflow(
        workflow_id: int,
        message: str,
        agent: str = "SYSTEM",
        state: WorkflowState | None = None,
    ) -> None:
        workflow = get_workflow(workflow_id)

        if workflow is None:
            return

        if workflow.current_state != "FAILED":
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="FAILED",
                error_message=message,
                agent=agent,
                action="WORKFLOW_FAILED",
            )

        if state is not None:
            save_checkpoint(
                state,
                status="FAILED",
                current_state="FAILED",
                error_message=message,
            )
        else:
            save_workflow_checkpoint(
                workflow_id=workflow_id,
                status="FAILED",
                current_state="FAILED",
                error_message=message,
            )

    def intake_node(
        state: WorkflowState,
    ) -> dict[str, Any]:
        result = intake_agent(
            state["workflow_input"]
        )

        if not result.get("success"):
            message = result.get(
                "message",
                "Intake failed.",
            )

            fail_workflow(
                workflow_id=state["workflow_id"],
                message=message,
                agent="intake_agent",
                state=state,
            )

            return {
                "intake_result": result,
                "status": "FAILED",
                "current_state": "FAILED",
                "error_message": message,
            }

        workflow = get_workflow(
            state["workflow_id"]
        )

        if workflow is not None:
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="PLANNING",
                agent="intake_agent",
                action="INTAKE_COMPLETED",
            )

        save_checkpoint(
            state,
            status="RUNNING",
            current_state="PLANNING",
            current_task_index=0,
            retry_count=0,
            error_message=None,
        )

        return {
            "intake_result": result,
            "status": "RUNNING",
            "current_state": "PLANNING",
            "error_message": None,
        }

    def planning_node(
        state: WorkflowState,
    ) -> dict[str, Any]:
        result = planning_agent(
            state["intake_result"]
        )

        if not result.get("success"):
            message = result.get(
                "message",
                "Planning failed.",
            )

            fail_workflow(
                workflow_id=state["workflow_id"],
                message=message,
                agent="planning_agent",
                state=state,
            )

            return {
                "planning_result": result,
                "status": "FAILED",
                "current_state": "FAILED",
                "error_message": message,
            }

        workflow = get_workflow(
            state["workflow_id"]
        )

        if workflow is not None:
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="EXECUTION",
                agent="planning_agent",
                action="PLANNING_COMPLETED",
            )

        tasks = result.get(
            "tasks",
            [],
        )

        save_checkpoint(
            state,
            status="RUNNING",
            current_state="EXECUTION",
            current_task_index=0,
            retry_count=0,
            approval_id=None,
            error_message=None,
            tasks=tasks,
            execution_results=[],
            review_results=[],
        )

        return {
            "planning_result": result,
            "tasks": tasks,
            "current_task_index": 0,
            "execution_results": [],
            "review_results": [],
            "approval_granted": state.get(
                "approval_granted",
                False,
            ),
            "approval_id": state.get(
                "approval_id"
            ),
            "status": "RUNNING",
            "current_state": "EXECUTION",
            "error_message": None,
        }

    def execution_node(
        state: WorkflowState,
    ) -> dict[str, Any]:
        tasks = state.get(
            "tasks",
            [],
        )

        current_index = state.get(
            "current_task_index",
            0,
        )

        approval_granted = state.get(
            "approval_granted",
            False,
        )

        execution_results = list(
            state.get(
                "execution_results",
                [],
            )
        )

        if current_index >= len(tasks):
            save_checkpoint(
                state,
                status="RUNNING",
                current_state="EXECUTION",
                current_task_index=current_index,
                tasks=tasks,
                execution_results=execution_results,
                error_message=None,
            )

            return {
                "status": "RUNNING",
                "current_state": "EXECUTION",
            }

        task_data = tasks[current_index]

        requires_approval = task_data.get(
            "requires_approval",
            False,
        )

        if requires_approval and not approval_granted:
            approval = create_approval(
                db=db,
                workflow_id=state["workflow_id"],
                task_id=None,
                requested_by="workflow_orchestrator",
            )

            workflow = get_workflow(
                state["workflow_id"]
            )

            if workflow is not None:
                transition_workflow(
                    db=db,
                    workflow=workflow,
                    next_state="APPROVAL",
                    agent="workflow_orchestrator",
                    action="APPROVAL_REQUIRED",
                )

            save_checkpoint(
                state,
                status="PENDING_APPROVAL",
                current_state="APPROVAL",
                current_task_index=current_index,
                approval_id=approval.id,
                tasks=tasks,
                execution_results=execution_results,
                error_message=None,
            )

            return {
                "status": "PENDING_APPROVAL",
                "current_state": "APPROVAL",
                "approval_id": approval.id,
                "error_message": None,
            }

        result = execute_task_with_retry(
            db=db,
            workflow_id=state["workflow_id"],
            task_data=task_data,
        )

        execution_results.append(
            result
        )

        if not result.get("success"):
            message = result.get(
                "message",
                "Task execution failed.",
            )

            fail_workflow(
                workflow_id=state["workflow_id"],
                message=message,
                agent="execution_agent",
                state={
                    **state,
                    "tasks": tasks,
                    "execution_results": execution_results,
                    "current_task_index": current_index,
                },
            )

            return {
                "execution_results": execution_results,
                "status": "FAILED",
                "current_state": "FAILED",
                "error_message": message,
            }

        next_task_index = current_index + 1

        save_checkpoint(
            state,
            status="RUNNING",
            current_state="EXECUTION",
            current_task_index=next_task_index,
            retry_count=result.get(
                "retry_count",
                0,
            ),
            approval_id=None,
            tasks=tasks,
            execution_results=execution_results,
            error_message=None,
        )

        return {
            "execution_results": execution_results,
            "current_task_index": next_task_index,
            "status": "RUNNING",
            "current_state": "EXECUTION",
            "approval_granted": False,
        }

    def execution_router(
        state: WorkflowState,
    ) -> str:
        if state.get(
            "status"
        ) == "PENDING_APPROVAL":
            return "approval"

        if state.get(
            "status"
        ) == "FAILED":
            return "failed"

        tasks = state.get(
            "tasks",
            [],
        )

        current_index = state.get(
            "current_task_index",
            0,
        )

        if current_index < len(tasks):
            return "next"

        workflow = get_workflow(
            state["workflow_id"]
        )

        if workflow is not None:
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="REVIEW",
                agent="workflow_orchestrator",
                action="EXECUTION_COMPLETED",
            )

        save_checkpoint(
            state,
            status="RUNNING",
            current_state="REVIEW",
            current_task_index=current_index,
            tasks=tasks,
            execution_results=state.get(
                "execution_results",
                [],
            ),
            error_message=None,
        )

        return "review"

    def review_node(
        state: WorkflowState,
    ) -> dict[str, Any]:
        execution_results = state.get(
            "execution_results",
            []
        )

        review_results = []

        for result in execution_results:
            review_result = review_agent(
                result
            )

            review_results.append(
                review_result
            )

        all_approved = all(
            result.get(
                "approved",
                False,
            )
            for result in review_results
        )

        if not all_approved:
            message = (
                "One or more execution results "
                "failed review."
            )

            fail_workflow(
                workflow_id=state["workflow_id"],
                message=message,
                agent="review_agent",
                state={
                    **state,
                    "review_results": review_results,
                },
            )

            return {
                "review_results": review_results,
                "status": "FAILED",
                "current_state": "FAILED",
                "error_message": message,
            }

        workflow = get_workflow(
            state["workflow_id"]
        )

        if workflow is not None:
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="COMPLETED",
                agent="review_agent",
                action="REVIEW_COMPLETED",
            )

        clear_workflow_checkpoint(
            state["workflow_id"]
        )

        create_audit_log(
            db=db,
            workflow_id=state["workflow_id"],
            agent="SYSTEM",
            action="CHECKPOINT_CLEARED",
            status="SUCCESS",
            message=(
                "Redis workflow checkpoint "
                "cleared after successful completion."
            ),
        )

        return {
            "review_results": review_results,
            "status": "COMPLETED",
            "current_state": "COMPLETED",
            "error_message": None,
        }

    graph = StateGraph(
        WorkflowState
    )

    graph.add_node(
        "intake",
        intake_node,
    )

    graph.add_node(
        "planning",
        planning_node,
    )

    graph.add_node(
        "execution",
        execution_node,
    )

    graph.add_node(
        "review",
        review_node,
    )

    graph.add_edge(
        START,
        "intake",
    )

    graph.add_edge(
        "intake",
        "planning",
    )

    graph.add_edge(
        "planning",
        "execution",
    )

    graph.add_conditional_edges(
        "execution",
        execution_router,
        {
            "next": "execution",
            "review": "review",
            "approval": END,
            "failed": END,
        },
    )

    graph.add_edge(
        "review",
        END,
    )

    return graph.compile()