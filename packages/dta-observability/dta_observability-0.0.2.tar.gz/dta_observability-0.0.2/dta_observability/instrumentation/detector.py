"""
Utilities for detecting installed packages.
"""

import importlib.util
from typing import Optional


class InstrumentationMap:
    """Registry of available instrumentations and their module paths."""

    LIBRARIES = {
        "asyncio": "opentelemetry.instrumentation.asyncio",
        "django": "opentelemetry.instrumentation.django",
        "tornado": "opentelemetry.instrumentation.tornado",
        "urllib": "opentelemetry.instrumentation.urllib",
        "aiohttp": "opentelemetry.instrumentation.aiohttp",
        "sqlalchemy": "opentelemetry.instrumentation.sqlalchemy",
        "psycopg2": "opentelemetry.instrumentation.psycopg2",
        "pymongo": "opentelemetry.instrumentation.pymongo",
        "asyncpg": "opentelemetry.instrumentation.asyncpg",
        "boto": "opentelemetry.instrumentation.boto",
        "botocore": "opentelemetry.instrumentation.botocore",
        "grpc": "opentelemetry.instrumentation.grpc",
        "jinja2": "opentelemetry.instrumentation.jinja2",
        "threading": "opentelemetry.instrumentation.threading",
    }

    SPECIAL_CLASS_NAMES = {
        "sqlalchemy": "SQLAlchemyInstrumentor",
    }

    @classmethod
    def get_module_path(cls, library_name: str) -> Optional[str]:
        """
        Get the instrumentation module path for a library.

        Args:
            library_name: The name of the library

        Returns:
            The module path or None if not found
        """
        return cls.LIBRARIES.get(library_name)

    @classmethod
    def get_instrumentor_class_name(cls, library_name: str) -> str:
        """
        Get the instrumentor class name for a library.

        Args:
            library_name: The name of the library

        Returns:
            The name of the instrumentor class
        """
        return cls.SPECIAL_CLASS_NAMES.get(library_name, f"{library_name.capitalize()}Instrumentor")


class PackageDetector:
    """Utilities for detecting installed packages."""

    @staticmethod
    def is_available(package_name: str) -> bool:
        """
        Check if a package is available for import.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if the package is available, False otherwise.
        """
        try:
            spec = importlib.util.find_spec(package_name)
            return spec is not None
        except (ImportError, ValueError):
            return False
