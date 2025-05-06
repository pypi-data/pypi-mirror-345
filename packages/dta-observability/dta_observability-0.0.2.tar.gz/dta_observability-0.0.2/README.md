# DTA Observability

A lightweight wrapper around OpenTelemetry for Python applications.

## Overview

DTA Observability simplifies the use of OpenTelemetry by providing a streamlined interface for instrumentation. It handles configuration of tracing, metrics, and logging with minimal setup.

## Features

- Single function initialization of all telemetry components
- Automatic instrumentation for Flask, FastAPI, Celery, and other frameworks
- Structured logging with trace context correlation
- Function decoration for easy span creation
- System and application metrics collection
- Support for OTLP and console exporters
- Automatic resource detection
- Configuration via parameters or environment variables

## Installation

```bash
pip install dta-observability
```

Or with Poetry:

```bash
poetry add dta-observability
```

## Basic Usage

```python
import dta_observability
from dta_observability import get_logger, traced

# Initialize telemetry
dta_observability.init_telemetry(
    service_name="my-service",
    service_version="1.0.0",
    otlp_endpoint="http://otel-collector:4317",
)

# Get a logger
logger = get_logger("my-service")

# Use the traced decorator
@traced(name="my_function")
def my_function():
    logger.info("Doing work")
    return "result"

# Create spans manually
with dta_observability.create_span("operation"):
    logger.info("Performing operation")
```

## Framework Integration

### Flask

```python
from flask import Flask
import dta_observability

app = Flask(__name__)

dta_observability.init_telemetry(
    service_name="flask-service",
    flask_app=app
)
```

### FastAPI

```python
from fastapi import FastAPI
import dta_observability

app = FastAPI()

dta_observability.init_telemetry(
    service_name="fastapi-service",
    fastapi_app=app
)
```

### Celery

```python
from celery import Celery
import dta_observability

app = Celery("tasks")

dta_observability.init_telemetry(
    service_name="worker-service",
    celery_app=app
)
```

## Configuration

Configuration options available in `init_telemetry()`:

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| service_name | SERVICE_NAME | unnamed-service | Name to identify the service |
| service_version | SERVICE_VERSION | 0.0.0 | Version of the service |
| service_instance_id | SERVICE_INSTANCE_ID | | Unique identifier for this service instance |
| resource_attributes | | None | Additional resource attributes (dictionary) |
| configure_auto_instrumentation | AUTO_INSTRUMENTATION_ENABLED | True | Whether to auto-instrument detected libraries |
| log_level | LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| flask_app | | None | Flask application instance to instrument |
| fastapi_app | | None | FastAPI application instance to instrument |
| celery_app | | None | Celery application instance to instrument |
| safe_logging | SAFE_LOGGING | True | Whether to enable safe logging with complex data types |
| excluded_instrumentations | EXCLUDED_INSTRUMENTATIONS | None | Comma-separated list of instrumentations to exclude |
| otlp_endpoint | EXPORTER_OTLP_ENDPOINT | http://localhost:4317 | OTLP exporter endpoint URL |
| otlp_insecure | EXPORTER_OTLP_INSECURE | True | Whether to use insecure connection for OTLP |
| batch_export_delay_ms | BATCH_EXPORT_SCHEDULE_DELAY | 5000 | Milliseconds between batch exports |
| enable_resource_detectors | RESOURCE_DETECTORS_ENABLED | True | Whether to enable automatic resource detection |
| enable_logging_instrumentation | LOGGING_INSTRUMENTATION_ENABLED | True | Whether to enable logging instrumentation |
| propagators | OTEL_PROPAGATORS | w3c,gcp,tracecontext | Comma-separated list of context propagators |
| exporter_type | EXPORTER_TYPE | otlp | Default exporter type for all signals (otlp or console) |
| traces_exporter_type | TRACES_EXPORTER | otlp | Exporter type for traces (otlp or console) |
| metrics_exporter_type | METRICS_EXPORTER | otlp | Exporter type for metrics (otlp or console) |
| logs_exporter_type | LOGS_EXPORTER | otlp | Exporter type for logs (otlp or console) |
| enable_traces | | True | Whether to enable trace collection |
| enable_metrics | | True | Whether to enable metrics collection |
| enable_logs | | True | Whether to enable logs collection |
| enable_system_metrics | SYSTEM_METRICS_ENABLED | True | Whether to enable system metrics collection |

Environment variables can also be prefixed with `OTEL_` or `DTA_` (e.g., `DTA_SERVICE_NAME`).

## Examples

The [examples](./examples) directory contains sample applications demonstrating usage with different frameworks.