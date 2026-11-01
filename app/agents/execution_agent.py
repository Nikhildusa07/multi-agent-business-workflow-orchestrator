from typing import Any

from app.observability.telemetry import tracer


def execution_agent(task: dict[str, Any]) -> dict[str, Any]:
    with tracer.start_as_current_span("execution_agent") as span:
        action = task.get("action")
        task_name = task.get("task_name", "Unknown task")

        span.set_attribute("agent.name", "execution_agent")
        span.set_attribute("task.name", task_name)
        span.set_attribute("task.action", str(action))

        if not action:
            span.set_attribute("result", "failed")

            return {
                "success": False,
                "task_name": task_name,
                "message": "No execution action provided.",
            }

        results = {
            "collect_data": {
                "message": "Business data collected successfully.",
                "data": {
                    "revenue": 125000,
                    "expenses": 85000,
                    "customers": 1250,
                },
            },
            "analyze_data": {
                "message": "Business performance analyzed successfully.",
                "analysis": {
                    "profit": 40000,
                    "customer_count": 1250,
                    "performance": "positive",
                },
            },
            "generate_report": {
                "message": "Business report generated successfully.",
                "report_status": "generated",
            },
            "prepare_message": {
                "message": "Communication content prepared successfully."
            },
            "review_message": {
                "message": "Communication prepared for review."
            },
            "analyze_customer_request": {
                "message": "Customer request analyzed successfully."
            },
            "prepare_response": {
                "message": "Customer support response prepared successfully."
            },
            "review_response": {
                "message": "Customer response prepared for review."
            },
            "execute_request": {
                "message": "Business request executed successfully."
            },
            "review_result": {
                "message": "Execution result prepared for review."
            },
        }

        result = results.get(action)

        if result is None:
            span.set_attribute("result", "failed")

            return {
                "success": False,
                "task_name": task_name,
                "message": f"Unsupported action: {action}",
            }

        span.set_attribute("result", "success")

        return {
            "success": True,
            "task_name": task_name,
            "action": action,
            **result,
        }