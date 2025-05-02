"""
Base classes for script engine namespaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseNamespace(ABC):
    """
    Base class for namespaces that can generate output after script execution.

    Namespaces that inherit from this class can implement the generate_output method
    to provide a final result after a script run is complete.
    """
    key:str

    def __init__(self, shared: dict[str, Any]):
        self.shared = shared

    @classmethod
    def generate_output(self) -> Optional[Any]:
        """
        Generate the final output for this namespace after script execution.

        Returns:
            The namespace's output data, or None if no output is available.
        """
        pass

    @classmethod
    def generate_metadata(self) -> Optional[Any]:
        """
        Generate the final output for this namespace after script execution.

        Returns:
            The namespace's metadata data, or None if no output is available.
        """
        pass
