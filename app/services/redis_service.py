import json

import redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


WORKFLOW_STATE_TTL = 86400


def set_workflow_state(
    workflow_id: int,
    state: dict,
    expire_seconds: int = WORKFLOW_STATE_TTL,
) -> bool:
    key = f"workflow:{workflow_id}:state"

    redis_client.set(
        key,
        json.dumps(state),
        ex=expire_seconds,
    )

    return True


def get_workflow_state(
    workflow_id: int,
) -> dict | None:
    key = f"workflow:{workflow_id}:state"

    data = redis_client.get(key)

    if data is None:
        return None

    return json.loads(data)


def delete_workflow_state(
    workflow_id: int,
) -> bool:
    key = f"workflow:{workflow_id}:state"

    redis_client.delete(key)

    return True


def set_workflow_status(
    workflow_id: int,
    status: str,
) -> bool:
    key = f"workflow:{workflow_id}:status"

    redis_client.set(
        key,
        status,
        ex=WORKFLOW_STATE_TTL,
    )

    return True


def get_workflow_status(
    workflow_id: int,
) -> str | None:
    key = f"workflow:{workflow_id}:status"

    return redis_client.get(key)


def save_workflow_checkpoint(
    workflow_id: int,
    *,
    status: str,
    current_state: str,
    current_task_index: int = 0,
    retry_count: int = 0,
    approval_id: int | None = None,
    error_message: str | None = None,
    tasks: list[dict] | None = None,
    execution_results: list[dict] | None = None,
    review_results: list[dict] | None = None,
    workflow_input: dict | None = None,
) -> bool:
    """
    Save the complete workflow execution checkpoint
    required for recovery.
    """

    state = {
        "workflow_id": workflow_id,
        "status": status,
        "current_state": current_state,
        "current_task_index": current_task_index,
        "retry_count": retry_count,
        "approval_id": approval_id,
        "error_message": error_message,
        "tasks": tasks or [],
        "execution_results": execution_results or [],
        "review_results": review_results or [],
        "workflow_input": workflow_input or {},
    }

    set_workflow_state(
        workflow_id=workflow_id,
        state=state,
    )

    set_workflow_status(
        workflow_id=workflow_id,
        status=status,
    )

    return True


def get_workflow_checkpoint(
    workflow_id: int,
) -> dict | None:
    return get_workflow_state(workflow_id)


def clear_workflow_checkpoint(
    workflow_id: int,
) -> bool:
    delete_workflow_state(
        workflow_id
    )

    redis_client.delete(
        f"workflow:{workflow_id}:status"
    )

    return True


def redis_health_check() -> bool:
    try:
        return bool(redis_client.ping())
    except Exception:
        return False