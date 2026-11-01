from app.services.cache_service import (
    set_workflow_state,
    get_workflow_state,
    delete_workflow_state,
)

workflow_id = 1

state = {
    "status": "EXECUTION",
    "current_task": "Analyze business performance",
}

set_workflow_state(workflow_id, state)

result = get_workflow_state(workflow_id)

print("\n===== REDIS WORKFLOW STATE =====")
print(result)

delete_workflow_state(workflow_id)

print("\nRedis workflow state test successful!")