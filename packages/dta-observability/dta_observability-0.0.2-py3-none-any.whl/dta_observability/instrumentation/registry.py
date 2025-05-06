"""
Registry for tracking instrumentation status.
Ensures we don't instrument the same library or application multiple times.
"""

import threading
from typing import Any, Dict


class InstrumentationRegistry:
    """
    Global registry for tracking instrumentation status across processes.
    Implemented as a thread-safe singleton to ensure consistent state.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "InstrumentationRegistry":
        """Ensure singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(InstrumentationRegistry, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self) -> None:
        """Initialize the registry data structures."""

        self._registry: Dict[str, Dict[str, Any]] = {}

    def is_globally_instrumented(self, library_name: str) -> bool:
        """
        Check if a library is already globally instrumented.

        Args:
            library_name: The name of the library to check

        Returns:
            True if globally instrumented, False otherwise
        """
        library_info = self._registry.get(library_name, {})
        return library_info.get("global", False)

    def set_globally_instrumented(self, library_name: str) -> None:
        """
        Mark a library as globally instrumented.

        Args:
            library_name: The name of the library to mark
        """
        if library_name not in self._registry:
            self._registry[library_name] = {"global": True, "apps": set()}
        else:
            self._registry[library_name]["global"] = True

    def is_app_instrumented(self, library_name: str, app: Any) -> bool:
        """
        Check if a specific app instance is already instrumented.

        Args:
            library_name: The name of the library
            app: The application instance

        Returns:
            True if already instrumented, False otherwise
        """
        library_info = self._registry.get(library_name, {})
        apps = library_info.get("apps", set())
        return app in apps

    def register_app(self, library_name: str, app: Any) -> None:
        """
        Register an app as instrumented.

        Args:
            library_name: The name of the library
            app: The application instance to register
        """
        if library_name not in self._registry:
            self._registry[library_name] = {"global": False, "apps": {app}}
        else:
            self._registry[library_name]["apps"].add(app)


instrumentation_registry = InstrumentationRegistry()
