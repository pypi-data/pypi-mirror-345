from typing import Any, List, override

import numpy as np

from ..namespaces.base import BaseNamespace

class ChartNamespace(BaseNamespace):
    """Handles chart drawing and plotting operations."""
    key = 'chart'

    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)  
        self._plots = []

    def plot(self, series: Any, title: str = '', color: str = '#000000', linewidth: int = 1) -> None:
        """Plot a series on the chart."""
        
        if isinstance(series, (float, int, np.number)) or series is None:
            data = {
                'bar': self.shared.get('data',{}).get('current'),
                'value': series
            }
            
            self._plots.append({
                'data': data,
                'options': {
                    'title': title,
                    'color': color,
                    'linewidth': linewidth
                }
            })
        else:
            raise TypeError("series must be a float, int, or None")

    def line(self, price: float, **kwargs) -> None:
        """Draw a horizontal line on the chart."""
        self._plots.append({
            'type': 'line',
            'price': price,
            'options': kwargs
        })

    def get_plots(self) -> List[dict]:
        """Get all registered plots for rendering."""
        return self._plots

    @override
    def generate_output(self) -> List[dict]:
        """Generate the final output for this namespace after script execution.

        Returns:
            A list of plot configurations for rendering.
        """
        return self.get_plots()
