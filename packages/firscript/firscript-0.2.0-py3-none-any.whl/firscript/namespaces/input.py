from typing import Any, Dict, override
from ..namespaces.base import BaseNamespace

class InputMetadata:
    def __init__(self, name: str, default: Any, type: str):
        self.name = name
        self.default = default
        self.type = type

class InputNamespace(BaseNamespace):
    """Handles script input parameters."""
    key = 'input'
    
    def __init__(self, shared: dict[str, Any], inputs: Dict[str, Any]):
        super().__init__(shared)
        
        self._inputs = inputs
        self._definedInputs: Dict[str, InputMetadata] = {}

    def int(self, name: str, default: int, **kwargs) -> int:
        """Get integer input parameter."""
        if name in self._definedInputs:
            raise ValueError(f"Input '{name}' already defined.")
        self._definedInputs.setdefault(name, InputMetadata(name, default, 'int'))
        return int(self._inputs.get(name, default))

    def float(self, name: str, default: float, **kwargs) -> float:
        """Get float input parameter."""
        if name in self._definedInputs:
            raise ValueError(f"Input '{name}' already defined.")
        self._definedInputs.setdefault(name, InputMetadata(name, default, 'float'))        
        return float(self._inputs.get(name, default))

    def text(self, name: str, default: str, **kwargs) -> str:
        """Get text input parameter."""
        if name in self._definedInputs:
            raise ValueError(f"Input '{name}' already defined.")
        self._definedInputs.setdefault(name, InputMetadata(name, default, 'text'))        
        return self._inputs.get(name, default)

    def bool(self, name: str, default: bool, **kwargs) -> bool:
        """Get boolean input parameter."""
        if name in self._definedInputs:
            raise ValueError(f"Input '{name}' already defined.")        
        self._definedInputs.setdefault(name, InputMetadata(name, default, 'bool'))        
        return bool(self._inputs.get(name, default))
    
    @override
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate the final output for this namespace after script execution.

        Returns:
            A dictionary containing the strategy's current state and orders.
        """
        return self._definedInputs