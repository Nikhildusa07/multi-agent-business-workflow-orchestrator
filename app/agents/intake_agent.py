from typing import Any

from app.observability.telemetry import tracer


def intake_agent(workflow_input: dict[str, Any]) -> dict[str, Any]:
    with tracer.start_as_current_span("intake_agent") as span:
        request = workflow_input.get("request", "").strip()

        span.set_attribute("agent.name", "intake_agent")

        if not request:
            span.set_attribute("result", "failed")
            return {
                "success": False,
                "message": "No workflow request provided.",
                "category": "unknown",
                "priority": workflow_input.get("priority", "normal"),
            }

        request_lower = request.lower()

        if any(
            keyword in request_lower
            for keyword in ["report", "analysis", "analyze", "performance"]
        ):
            category = "business_analysis"
        elif any(
            keyword in request_lower
            for keyword in ["email", "mail", "message"]
        ):
            category = "communication"
        elif any(
            keyword in request_lower
            for keyword in ["customer", "support", "ticket"]
        ):
            category = "customer_support"
        else:
            category = "general_business"

        priority = workflow_input.get("priority", "normal")

        span.set_attribute("workflow.category", category)
        span.set_attribute("workflow.priority", priority)
        span.set_attribute("result", "success")

        return {
            "success": True,
            "message": "Request successfully classified.",
            "request": request,
            "category": category,
            "priority": priority,
        }