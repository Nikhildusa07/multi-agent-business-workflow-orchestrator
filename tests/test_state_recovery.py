from app.services.redis_service import (
    clear_workflow_checkpoint,
    get_workflow_checkpoint,
    save_workflow_checkpoint,
)


def test_workflow_checkpoint_recovery():
    workflow_id = 9999

    clear_workflow_checkpoint(workflow_id)

    save_workflow_checkpoint(
        workflow_id=workflow_id,
        status="RUNNING",
        current_state="EXECUTION",
        current_task_index=2,
        retry_count=1,
        approval_id=None,
        error_message=None,
    )

    checkpoint = get_workflow_checkpoint(
        workflow_id
    )

    assert checkpoint is not None
    assert checkpoint["workflow_id"] == workflow_id
    assert checkpoint["status"] == "RUNNING"
    assert checkpoint["current_state"] == "EXECUTION"
    assert checkpoint["current_task_index"] == 2
    assert checkpoint["retry_count"] == 1
    assert checkpoint["approval_id"] is None
    assert checkpoint["error_message"] is None

    clear_workflow_checkpoint(workflow_id)

    checkpoint_after_clear = (
        get_workflow_checkpoint(workflow_id)
    )

    assert checkpoint_after_clear is None