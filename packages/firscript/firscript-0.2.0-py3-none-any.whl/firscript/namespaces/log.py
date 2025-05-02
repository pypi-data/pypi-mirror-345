from typing import Any, List, override, Optional

from .base import BaseNamespace


class LogNamespace(BaseNamespace):
    """Handles logging operations."""
    key = 'log'
    
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        
        self._info_logs: List[str] = []        
        self._warning_logs: List[str] = []
        self._error_logs: List[str] = []

    def info(self, message: str) -> None:
        """Log an informational message."""
        self._info_logs.append(message)        

    def error(self, message: str) -> None:
        """Log an error message."""
        self._error_logs.append(message)        
        
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._warning_logs.append(message)        
    
    @override
    def generate_output(self) -> Optional[dict[str, List[str]]]:
        """Generate the final output for this namespace after script execution.

        Returns:
            A dictionary of logged messages.
        """
        return {
            'info': self._info_logs,
            'warning': self._warning_logs,
            'error': self._error_logs
        }