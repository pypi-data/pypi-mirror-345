"""
Base Adapter interface for ObservAI.

Each adapter encapsulates logic to detect and instrument a specific SDK (e.g., OpenAI SDK).
"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod

class Adapter(ABC):
    """
    Abstract base class for all ObservAI adapters.

    Subclasses must implement:
      - is_available(): detect if the target SDK is installed
      - patch(): apply instrumentation (e.g., monkey-patch functions)
    """
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Return True if the target library is present and should be instrumented."""
        ...

    @abstractmethod
    def patch(self) -> None:
        """Apply instrumentation to the target library."""
        ...
