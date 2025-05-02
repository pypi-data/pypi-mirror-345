from typing import Any
from ..namespaces.base import BaseNamespace


class ColorNamespace(BaseNamespace):
    """Provides color constants and utilities."""
    key = 'color'
    
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        
        self._colors = {
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'black': '#000000',
            'white': '#FFFFFF',
            'gray': '#808080',
            'orange': '#FFA500',
            'purple': '#800080',
            'pink': '#FFC0CB'
        }

    def __getattr__(self, name: str) -> str:
        """Get color by name."""
        if name in self._colors:
            return self._colors[name]
        raise AttributeError(f"No color named '{name}'")

    def rgb(self, r: int, g: int, b: int) -> str:
        """Create RGB color string."""
        return f"#{r:02x}{g:02x}{b:02x}"