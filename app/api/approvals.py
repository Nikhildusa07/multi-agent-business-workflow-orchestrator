from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.approval import Approval
from app.models.workflow import Workflow
from app.orchestration.graph import build_workflow_graph
from app.orchestration.state import WorkflowState
from app.orchestration.transitions import (
    InvalidStateTransition,
    transition_workflow,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


class ApprovalAction(BaseModel):
    approved_by: str


@router.get("/")
def get_approvals(
    db: Session = Depends(get_db),
):
    return (
        db.query(Approval)
        .order_by(Approval.id.desc())
        .all()
    )


@router.post("/{approval_id}/approve")
def approve_request(
    approval_id: int,
    data: ApprovalAction,
    db: Session = Depends(get_db),
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Approval is already "
                f"{approval.status}"
            ),
        )

    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == approval.workflow_id
        )
        .first()
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Associated workflow not found",
        )

    if workflow.current_state != "APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=(
                "Workflow is not waiting for approval. "
                f"Current state: "
                f"{workflow.current_state}"
            ),
        )

    try:
        approval.status = "APPROVED"
        approval.approved_by = data.approved_by
        approval.approved_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(approval)

        create_audit_log(
            db=db,
            workflow_id=approval.workflow_id,
            task_id=approval.task_id,
            agent="human_approval",
            action="APPROVAL_GRANTED",
            status="SUCCESS",
            message=(
                f"Approved by "
                f"{data.approved_by}"
            ),
        )

        transition_workflow(
            db=db,
            workflow=workflow,
            next_state="EXECUTION",
            agent="human_approval",
            action="APPROVAL_RESUMED",
        )

        initial_state: WorkflowState = {
            "workflow_id": workflow.id,
            "workflow_input": workflow.input_data,
            "status": "RUNNING",
            "current_state": "EXECUTION",
            "retry_count": 0,
            "max_retries": 3,
            "current_task_index": 0,
            "tasks": [],
            "execution_results": [],
            "review_results": [],
            "approval_granted": True,
            "approval_id": approval.id,
            "error_message": None,
        }

        workflow_graph = build_workflow_graph(db)

        result = workflow_graph.invoke(
            initial_state
        )

        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == approval.workflow_id
            )
            .first()
        )

        if workflow is not None:
            workflow.status = result.get(
                "status",
                workflow.status,
            )

            workflow.current_state = result.get(
                "current_state",
                workflow.current_state,
            )

            workflow.error_message = result.get(
                "error_message"
            )

            db.commit()
            db.refresh(workflow)

        return {
            "message": (
                "Approval granted and "
                "workflow resumed."
            ),
            "approval": approval,
            "workflow": workflow,
        }

    except InvalidStateTransition as exc:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception as exc:
        db.rollback()

        workflow = (
            db.query(Workflow)
            .filter(
                Workflow.id == approval.workflow_id
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
                        agent="SYSTEM",
                        action="WORKFLOW_FAILED_AFTER_APPROVAL",
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
                "Workflow execution after "
                f"approval failed: {exc}"
            ),
        )


@router.post("/{approval_id}/reject")
def reject_request(
    approval_id: int,
    data: ApprovalAction,
    db: Session = Depends(get_db),
):
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Approval is already "
                f"{approval.status}"
            ),
        )

    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == approval.workflow_id
        )
        .first()
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Associated workflow not found",
        )

    if workflow.current_state != "APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=(
                "Workflow is not waiting for approval. "
                f"Current state: "
                f"{workflow.current_state}"
            ),
        )

    approval.status = "REJECTED"
    approval.approved_by = data.approved_by
    approval.approved_at = datetime.now(
        timezone.utc
    )

    workflow.status = "FAILED"
    workflow.current_state = "APPROVAL"
    workflow.error_message = (
        f"Workflow rejected by "
        f"{data.approved_by}."
    )

    db.commit()

    db.refresh(approval)
    db.refresh(workflow)

    create_audit_log(
        db=db,
        workflow_id=approval.workflow_id,
        task_id=approval.task_id,
        agent="human_approval",
        action="APPROVAL_REJECTED",
        status="REJECTED",
        message=(
            f"Rejected by "
            f"{data.approved_by}"
        ),
    )

    create_audit_log(
        db=db,
        workflow_id=workflow.id,
        agent="SYSTEM",
        action="WORKFLOW_REJECTED",
        status="FAILED",
        message=(
            "Workflow stopped because approval "
            f"was rejected by "
            f"{data.approved_by}."
        ),
    )

    return {
        "message": (
            "Approval rejected and "
            "workflow stopped."
        ),
        "approval": approval,
        "workflow": workflow,
    }