from fastapi import APIRouter
from app.observability.telemetry import tracer


router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


@router.get("/test")
def telemetry_test():
    with tracer.start_as_current_span("telemetry_test") as span:
        span.set_attribute("test.type", "manual")
        span.set_attribute("test.status", "success")

        return {
            "message": "OpenTelemetry trace created successfully",
            "status": "success",
        }