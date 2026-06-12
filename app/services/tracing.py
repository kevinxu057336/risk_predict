import os
import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

logger = logging.getLogger("risk_telemetry")

TRACING_ENABLED = os.getenv("RISK_TRACING_ENABLED", "false").lower() == "true"


def setup_tracing(app):
    if not TRACING_ENABLED:
        logger.info("链路追踪未启用（设置 RISK_TRACING_ENABLED=true 开启）")
        return

    resource = Resource.create({SERVICE_NAME: "risk-predict-api"})
    provider = TracerProvider(resource=resource)

    exporter_type = os.getenv("RISK_TRACE_EXPORTER", "console")
    if exporter_type == "console":
        exporter = ConsoleSpanExporter()
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry FastAPI 链路追踪已启用")
    except Exception as e:
        logger.warning("FastAPI 链路追踪插桩失败: %s", e)


def get_tracer():
    return trace.get_tracer("risk-predict-api")