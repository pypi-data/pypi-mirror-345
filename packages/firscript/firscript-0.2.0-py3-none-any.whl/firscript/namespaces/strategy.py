from typing import Any, Dict, override

from ..namespaces.base import BaseNamespace

class StrategyNamespace(BaseNamespace):
    """Handles strategy order management and position tracking."""
    key = 'strategy'

    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        
        self._orders = []
        self._position = None

    def long(self, **kwargs) -> None:
        """Enter a long position."""
        self._orders.append({
            'type': 'long',
            'options': kwargs
        })

    def short(self, **kwargs) -> None:
        """Enter a short position."""
        self._orders.append({
            'type': 'short',
            'options': kwargs
        })

    def close(self, **kwargs) -> None:
        """Close current position."""
        self._orders.append({
            'type': 'close',
            'options': kwargs
        })

    def position(self) -> dict:
        """Get current position info."""
        return self._position or {
            'size': 0,
            'entry_price': 0,
            'profit': 0
        }

    @override
    def generate_output(self) -> Dict[str, Any]:
        """Generate the final output for this namespace after script execution.

        Returns:
            A dictionary containing the strategy's current state and orders.
        """
        return {
            'position': self.position(),
            'orders': self._orders
        }