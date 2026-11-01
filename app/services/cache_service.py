import json
from typing import Any

from app.core.redis import redis_client


def set_workflow_state(
    workflow_id: int,
    state: dict[str, Any],
    expire_seconds: int = 3600,
) -> None:
    key = f"workflow:{workflow_id}:state"

    redis_client.set(
        key,
        json.dumps(state),
        ex=expire_seconds,
    )


def get_workflow_state(
    workflow_id: int,
) -> dict[str, Any] | None:
    key = f"workflow:{workflow_id}:state"

    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def delete_workflow_state(workflow_id: int) -> None:
    key = f"workflow:{workflow_id}:state"

    redis_client.delete(key)