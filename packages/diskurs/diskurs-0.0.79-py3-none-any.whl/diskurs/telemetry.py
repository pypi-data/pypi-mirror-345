import os
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# configure the SDK to export to OTLP endpoint
resource = Resource.create({SERVICE_NAME: "diskurs"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        headers={},
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# a module‐level tracer you can import everywhere
tracer = trace.get_tracer(__name__)
