from app.observability.telemetry import tracer


def main():
    with tracer.start_as_current_span("test-workflow") as span:
        span.set_attribute("workflow.id", 999)
        span.set_attribute("workflow.state", "TEST")

        with tracer.start_as_current_span("test-agent"):
            print("Intake trace created")

        print("Workflow trace created")


if __name__ == "__main__":
    main()