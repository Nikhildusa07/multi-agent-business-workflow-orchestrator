from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.orchestration.graph import build_workflow_graph
from app.orchestration.state import WorkflowState
from app.orchestration.transitions import (
    InvalidStateTransition,
    transition_workflow,
)
from app.services.audit_service import create_audit_log
from app.services.recovery_service import (
    can_recover_workflow,
    get_recovery_checkpoint,
)
from app.services.redis_service import (
    clear_workflow_checkpoint,
)


router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


@router.post(
    "/",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
):
    workflow = Workflow(
        workflow_name=workflow_data.workflow_name,
        input_data=workflow_data.input_data,
        status="PENDING",
        current_state="PENDING",
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    create_audit_log(
        db=db,
        workflow_id=workflow.id,
        agent="SYSTEM",
        action="WORKFLOW_CREATED",
        status="SUCCESS",
        message=(
            f"Workflow created: "
            f"{workflow.workflow_name}"
        ),
    )

    return workflow


@router.get(
    "/",
    response_model=list[WorkflowResponse],
)
def get_workflows(
    db: Session = Depends(get_db),
):
    return (
        db.query(Workflow)
        .order_by(Workflow.created_at.desc())
        .all()
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id)
        .first()
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow


def _execute_workflow(
    workflow: Workflow,
    db: Session,
    initial_state: WorkflowState,
):
    workflow_graph = build_workflow_graph(db)

    result = workflow_graph.invoke(
        initial_state
    )

    refreshed_workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == workflow.id
        )
        .first()
    )

    if refreshed_workflow is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Workflow not found after execution"
            ),
        )

    refreshed_workflow.status = result.get(
        "status",
        refreshed_workflow.status,
    )

    refreshed_workflow.current_state = result.get(
        "current_state",
        refreshed_workflow.current_state,
    )

    refreshed_workflow.error_message = result.get(
        "error_message"
    )

    db.commit()
    db.refresh(refreshed_workflow)

    return refreshed_workflow


@router.post(
    "/{workflow_id}/run",
    response_model=WorkflowResponse,
)
def run_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id)
        .first()
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    if workflow.status == "RUNNING":
        raise HTTPException(
            status_code=409,
            detail="Workflow is already running",
        )

    if workflow.status == "PENDING_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=(
                "Workflow is waiting for human approval"
            ),
        )

    if workflow.status == "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail="Workflow is already completed",
        )

    try:
        if workflow.current_state == "PENDING":
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="INTAKE",
                agent="SYSTEM",
                action="WORKFLOW_STARTED",
            )

        elif workflow.current_state == "FAILED":
            transition_workflow(
                db=db,
                workflow=workflow,
                next_state="INTAKE",
                error_message=None,
                agent="SYSTEM",
                action="WORKFLOW_RECOVERY",
            )

        else:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Workflow cannot be started from "
                    f"state {workflow.current_state}"
                ),
            )

        initial_state: WorkflowState = {
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

        return _execute_workflow(
            workflow=workflow,
            db=db,
            initial_state=initial_state,
        )

    except InvalidStateTransition as exc:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        workflow = (
            db.query(Workflow)
            .filter(Workflow.id == workflow_id)
            .first()
        )

        if workflow is not None:
            try:
                if workflow.current_state != "FAILED":
                    transition_workflow(
                        db=db,
                        workflow=workflow,
                        next_state="FAILED",
                        error_message=str(exc),
                        agent="SYSTEM",
                        action="WORKFLOW_FAILED",
                    )
                else:
                    workflow.error_message = str(exc)
                    db.commit()
                    db.refresh(workflow)

            except Exception:
                db.rollback()

                workflow.status = "FAILED"
                workflow.current_state = "FAILED"
                workflow.error_message = str(exc)

                db.commit()
                db.refresh(workflow)

        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {exc}",
        )


@router.post(
    "/{workflow_id}/recover",
    response_model=WorkflowResponse,
)
def recover_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id)
        .first()
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    if not can_recover_workflow(
        workflow_id
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "No recoverable Redis checkpoint "
                "exists for this workflow."
            ),
        )

    checkpoint = get_recovery_checkpoint(
        workflow_id
    )

    if checkpoint is None:
        raise HTTPException(
            status_code=409,
            detail="Recovery checkpoint not found.",
        )

    checkpoint_state = checkpoint.get(
        "current_state"
    )

    checkpoint_status = checkpoint.get(
        "status"
    )

    if checkpoint_state == "APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=(
                "Workflow is waiting for human approval. "
                "Use the approval endpoint to resume it."
            ),
        )

    if checkpoint_state == "FAILED":
        raise HTTPException(
            status_code=409,
            detail=(
                "Workflow has failed. "
                "Use the normal run endpoint to restart it."
            ),
        )

    try:
        if workflow.current_state != checkpoint_state:
            workflow.current_state = checkpoint_state

        workflow.status = checkpoint_status

        workflow.error_message = checkpoint.get(
            "error_message"
        )

        db.commit()
        db.refresh(workflow)

        create_audit_log(
            db=db,
            workflow_id=workflow.id,
            agent="recovery_service",
            action="WORKFLOW_RECOVERY_STARTED",
            status="SUCCESS",
            message=(
                "Workflow recovery started from "
                f"Redis checkpoint at state "
                f"{checkpoint_state}, task index "
                f"{checkpoint.get('current_task_index', 0)}."
            ),
        )

        recovery_state: WorkflowState = {
            "workflow_id": workflow.id,
            "workflow_input": workflow.input_data,
            "status": "RUNNING",
            "current_state": checkpoint_state,
            "retry_count": checkpoint.get(
                "retry_count",
                0,
            ),
            "max_retries": 3,
            "current_task_index": checkpoint.get(
                "current_task_index",
                0,
            ),
            "tasks": [],
            "execution_results": [],
            "review_results": [],
            "approval_granted": False,
            "approval_id": checkpoint.get(
                "approval_id"
            ),
            "error_message": checkpoint.get(
                "error_message"
            ),
        }

        if checkpoint_state != "INTAKE":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Checkpoint recovery requires "
                    "workflow task context that is not "
                    "currently persisted in Redis."
                ),
            )

        return _execute_workflow(
            workflow=workflow,
            db=db,
            initial_state=recovery_state,
        )

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == workflow_id
            )
            .first()
        )

        if workflow is not None:
            try:
                if workflow.current_state != "FAILED":
                    transition_workflow(
                        db=db,
                        workflow=workflow,
                        next_state="FAILED",
                        error_message=str(exc),
                        agent="recovery_service",
                        action="WORKFLOW_RECOVERY_FAILED",
                    )
                else:
                    workflow.error_message = str(exc)
                    db.commit()
                    db.refresh(workflow)
            except Exception:
                db.rollback()

                workflow.status = "FAILED"
                workflow.current_state = "FAILED"
                workflow.error_message = str(exc)

                db.commit()
                db.refresh(workflow)

        raise HTTPException(
            status_code=500,
            detail=(
                "Workflow recovery failed: "
                f"{exc}"
            ),
        )