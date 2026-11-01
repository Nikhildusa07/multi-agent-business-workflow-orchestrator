from app.agents.intake_agent import intake_agent
from app.agents.planning_agent import planning_agent
from app.agents.execution_agent import execution_agent
from app.agents.review_agent import review_agent


workflow_input = {
    "request": "Create a business performance report",
    "priority": "high",
}

intake_result = intake_agent(workflow_input)

print("\nINTAKE RESULT:")
print(intake_result)

planning_result = planning_agent(intake_result)

print("\nPLANNING RESULT:")
print(planning_result)

print("\nEXECUTION RESULTS:")

execution_results = []

for task in planning_result["tasks"]:
    result = execution_agent(task)
    execution_results.append(result)
    print(result)

print("\nREVIEW RESULTS:")

for result in execution_results:
    review_result = review_agent(result)
    print(review_result)