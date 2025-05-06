"""
Resource detection for DTA Observability.
"""

import importlib
import os
import socket
from typing import Any, Dict, Optional

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from dta_observability.core.config import ConfigValueType, get_boolean_config, get_typed_config
from dta_observability.logging.logger import get_logger

logger = get_logger("dta_observability.resources")


_DETECTED_RESOURCE_CACHE = None


def detect_resources(override_attrs: Optional[Dict[str, Any]] = None) -> Resource:
    """
    Detect resources from the environment.

    Args:
        override_attrs: Optional dictionary of attributes that override detected ones

    Returns:
        OpenTelemetry Resource with detected attributes.
    """
    global _DETECTED_RESOURCE_CACHE

    if _DETECTED_RESOURCE_CACHE is not None and override_attrs is None:
        logger.debug("Using cached resource detection result")
        return _DETECTED_RESOURCE_CACHE

    if not get_boolean_config("RESOURCE_DETECTORS_ENABLED", default=True):
        logger.debug("Resource detection disabled via configuration")
        resource = Resource(override_attrs or {})
        if override_attrs is None:
            _DETECTED_RESOURCE_CACHE = resource
        return resource

    attributes = {}

    service_name = get_typed_config("SERVICE_NAME", ConfigValueType.STRING, "unnamed-service")
    service_version = get_typed_config("SERVICE_VERSION", ConfigValueType.STRING, "0.0.0")
    service_instance_id = get_typed_config("SERVICE_INSTANCE_ID", ConfigValueType.STRING, socket.gethostname())

    attributes[ResourceAttributes.SERVICE_NAME] = service_name
    attributes[ResourceAttributes.SERVICE_VERSION] = service_version
    attributes[ResourceAttributes.SERVICE_INSTANCE_ID] = service_instance_id

    is_gcp = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

    if os.environ.get("KUBERNETES_SERVICE_HOST") and not is_gcp:
        attributes["cloud.provider"] = "kubernetes"
    elif os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"):
        attributes["cloud.provider"] = "aws"
    elif os.environ.get("AZURE_REGION") or os.environ.get("AZURE_LOCATION"):
        attributes["cloud.provider"] = "azure"

    user_overrides = {}
    if override_attrs:
        for key, value in override_attrs.items():
            if value is not None:
                user_overrides[key] = value

    if is_gcp:

        detector_class = None
        try:

            try:
                from opentelemetry.resourcedetector.gcp_resource_detector import GoogleCloudResourceDetector

                detector_class = GoogleCloudResourceDetector
                logger.debug("Using GoogleCloudResourceDetector from opentelemetry.resourcedetector")
            except ImportError:
                try:
                    module = importlib.import_module("opentelemetry_resourcedetector_gcp")
                    if hasattr(module, "GoogleCloudResourceDetector"):
                        detector_class = getattr(module, "GoogleCloudResourceDetector")
                        logger.debug("Using GoogleCloudResourceDetector from opentelemetry_resourcedetector_gcp")
                except ImportError:
                    logger.debug("GoogleCloudResourceDetector not available")

            if detector_class:

                detector = detector_class(raise_on_error=False)
                gcp_resource = detector.detect()

                if gcp_resource and gcp_resource.attributes:
                    logger.debug(f"GCP detector found attributes: {dict(gcp_resource.attributes)}")

                    base_resource = Resource.create(attributes)

                    final_resource = base_resource.merge(gcp_resource)

                    if user_overrides:
                        final_resource = final_resource.merge(Resource.create(user_overrides))

                    if override_attrs is None:
                        _DETECTED_RESOURCE_CACHE = final_resource

                    return final_resource
        except Exception as e:
            logger.warning(f"Error using GoogleCloudResourceDetector: {e}")

        logger.debug("Using fallback GCP resource detection")
        attributes["cloud.provider"] = "gcp"

        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        if project_id:
            attributes["cloud.account.id"] = project_id

        if os.environ.get("KUBERNETES_SERVICE_HOST"):
            attributes["cloud.platform"] = "gcp_kubernetes_engine"

            hostname = socket.gethostname()
            if "-" in hostname:
                parts = hostname.split("-")
                if len(parts) >= 3:
                    attributes["k8s.cluster.name"] = "-".join(parts[:-2])

            if os.environ.get("NAMESPACE"):
                attributes["k8s.namespace.name"] = os.environ.get("NAMESPACE")
            if os.environ.get("POD_NAME"):
                attributes["k8s.pod.name"] = os.environ.get("POD_NAME")
            if os.environ.get("CONTAINER_NAME"):
                attributes["k8s.container.name"] = os.environ.get("CONTAINER_NAME")

        elif os.environ.get("K_SERVICE"):
            attributes["cloud.platform"] = "gcp_cloud_run"
            attributes["faas.name"] = os.environ.get("K_SERVICE")
            if os.environ.get("K_REVISION"):
                attributes["faas.version"] = os.environ.get("K_REVISION")
            if os.environ.get("K_CONFIGURATION"):
                attributes["faas.instance"] = os.environ.get("K_CONFIGURATION")
        else:
            attributes["cloud.platform"] = "gcp_compute_engine"

    if override_attrs:
        for key, value in override_attrs.items():
            if value is not None:
                attributes[key] = value

    resource = Resource.create(attributes)
    logger.debug(f"Final resource attributes: {dict(resource.attributes)}")

    if override_attrs is None:
        _DETECTED_RESOURCE_CACHE = resource

    return resource
