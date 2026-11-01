from typing import Any

from app.observability.telemetry import tracer


def planning_agent(intake_result: dict[str, Any]) -> dict[str, Any]:
    with tracer.start_as_current_span("planning_agent") as span:
        span.set_attribute("agent.name", "planning_agent")

        if not intake_result.get("success"):
            span.set_attribute("result", "failed")

            return {
                "success": False,
                "message": "Planning cannot start because intake failed.",
                "tasks": [],
            }

        category = intake_result.get("category")
        request = intake_result.get("request")
        priority = intake_result.get("priority", "normal")

        if category == "business_analysis":
            tasks = [
                {
                    "task_name": "Collect business data",
                    "assigned_agent": "execution_agent",
                    "action": "collect_data",
                    "requires_approval": False,
                },
                {
                    "task_name": "Analyze business performance",
                    "assigned_agent": "execution_agent",
                    "action": "analyze_data",
                    "requires_approval": False,
                },
                {
                    "task_name": "Generate business report",
                    "assigned_agent": "execution_agent",
                    "action": "generate_report",
                    "requires_approval": False,
                },
            ]

        elif category == "communication":
            tasks = [
                {
                    "task_name": "Prepare communication content",
                    "assigned_agent": "execution_agent",
                    "action": "prepare_message",
                    "requires_approval": True,
                },
                {
                    "task_name": "Review communication",
                    "assigned_agent": "review_agent",
                    "action": "review_message",
                    "requires_approval": False,
                },
            ]

        elif category == "customer_support":
            tasks = [
                {
                    "task_name": "Analyze customer request",
                    "assigned_agent": "execution_agent",
                    "action": "analyze_customer_request",
                    "requires_approval": False,
                },
                {
                    "task_name": "Prepare support response",
                    "assigned_agent": "execution_agent",
                    "action": "prepare_response",
                    "requires_approval": True,
                },
                {
                    "task_name": "Review support response",
                    "assigned_agent": "review_agent",
                    "action": "review_response",
                    "requires_approval": False,
                },
            ]

        else:
            tasks = [
                {
                    "task_name": "Execute business request",
                    "assigned_agent": "execution_agent",
                    "action": "execute_request",
                    "requires_approval": True,
                },
                {
                    "task_name": "Review execution result",
                    "assigned_agent": "review_agent",
                    "action": "review_result",
                    "requires_approval": False,
                },
            ]

        approval_required = any(
            task.get("requires_approval", False)
            for task in tasks
        )

        span.set_attribute("workflow.category", category)
        span.set_attribute("workflow.task_count", len(tasks))
        span.set_attribute(
            "workflow.approval_required",
            approval_required,
        )
        span.set_attribute("result", "success")

        return {
            "success": True,
            "message": "Execution plan created successfully.",
            "request": request,
            "category": category,
            "priority": priority,
            "approval_required": approval_required,
            "tasks": tasks,
        }