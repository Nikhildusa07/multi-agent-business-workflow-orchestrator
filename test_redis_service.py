from app.services.redis_service import (
    set_workflow_state,
    get_workflow_state,
    set_workflow_status,
    get_workflow_status,
    delete_workflow_state,
)


workflow_id = 999

state = {
    "workflow_id": workflow_id,
    "current_state": "EXECUTION",
    "status": "RUNNING",
    "retry_count": 0,
}

print("\n===== REDIS WORKFLOW STATE TEST =====")

set_workflow_state(workflow_id, state)

print("Stored state:")
print(get_workflow_state(workflow_id))

set_workflow_status(workflow_id, "RUNNING")

print("\nStored status:")
print(get_workflow_status(workflow_id))

delete_workflow_state(workflow_id)

print("\nState after delete:")
print(get_workflow_state(workflow_id))

print("\nRedis service test completed.")
