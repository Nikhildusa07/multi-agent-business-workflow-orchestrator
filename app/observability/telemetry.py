from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


resource = Resource.create(
    {
        "service.name": "multi-agent-workflow-orchestrator",
        "service.version": "1.0.0",
    }
)

provider = TracerProvider(resource=resource)

provider.add_span_processor(
    SimpleSpanProcessor(
        ConsoleSpanExporter()
    )
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer(
    "multi-agent-workflow-orchestrator"
)