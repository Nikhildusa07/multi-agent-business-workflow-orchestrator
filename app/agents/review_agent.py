from typing import Any

from app.observability.telemetry import tracer


def review_agent(execution_result: dict[str, Any]) -> dict[str, Any]:
    with tracer.start_as_current_span("review_agent") as span:
        span.set_attribute("agent.name", "review_agent")

        if not execution_result.get("success"):
            span.set_attribute("decision", "RETRY")
            span.set_attribute("result", "failed")

            return {
                "success": False,
                "approved": False,
                "decision": "RETRY",
                "message": "Execution failed. Task should be retried.",
            }

        task_name = execution_result.get(
            "task_name",
            "Unknown task",
        )

        span.set_attribute("task.name", task_name)
        span.set_attribute("decision", "APPROVED")
        span.set_attribute("result", "success")

        return {
            "success": True,
            "approved": True,
            "decision": "APPROVED",
            "task_name": task_name,
            "message": "Execution result passed quality review.",
        }