from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    workflow_id: int
    workflow_input: dict[str, Any]

    intake_result: dict[str, Any]
    planning_result: dict[str, Any]

    tasks: list[dict[str, Any]]
    current_task_index: int

    execution_results: list[dict[str, Any]]
    review_results: list[dict[str, Any]]

    status: str
    current_state: str

    retry_count: int
    max_retries: int

    approval_granted: bool
    approval_id: int | None

    error_message: str | None