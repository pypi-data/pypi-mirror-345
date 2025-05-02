import logging
from types import FunctionType
from typing import Any, Callable, Dict, Optional

from firscript.namespaces.base import BaseNamespace
from firscript.namespaces.chart import ChartNamespace
from firscript.namespaces.color import ColorNamespace
from firscript.namespaces.data import DataNamespace
from firscript.namespaces.input import InputNamespace
from firscript.namespaces.log import LogNamespace
from firscript.namespaces.strategy import StrategyNamespace
from firscript.namespaces.ta import TANamespace

logger = logging.getLogger(__name__)

class NamespaceRegistry:
    def __init__(self):
        self.namespaces: Dict[str, BaseNamespace] = {}
        self.shared: dict[str, Any] = {}

    def register(self, name: str, namespace: BaseNamespace | Callable) -> None:
        if not isinstance(namespace, BaseNamespace) and not callable(namespace):
            raise ValueError(f"Namespace '{name}' must be an instance of BaseNamespace")
        self.namespaces[name] = namespace
        
    def register_default_namespaces(self, inputs_override: Optional[Dict[str, Any]], column_mapping: Optional[Dict[str, str]] = None) -> None:
        """Initialize and register the default namespaces."""
        self.register("ta", TANamespace(self.shared))
        self.register("input", InputNamespace(self.shared, inputs_override or {}))
        self.register("chart", ChartNamespace(self.shared))
        self.register("color", ColorNamespace(self.shared))
        self.register("strategy", StrategyNamespace(self.shared))
        self.register("data", DataNamespace(self.shared, column_mapping))
        self.register("log", LogNamespace(self.shared))        
        logger.debug("Default namespaces registered.")        

    def get(self, name: str) -> BaseNamespace:
        return self.namespaces[name]

    def build(self) -> dict[str, BaseNamespace]:
        return self.namespaces.copy()

    @staticmethod
    def generate_outputs(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
        outputs = {}
        for name, namespace in namespaces.items():
            if not isinstance(namespace, BaseNamespace):
                continue
            output = namespace.generate_output()
            if output is not None:
                outputs[name] = output
        return outputs
    
    @staticmethod
    def generate_metadatas(namespaces: dict[str, BaseNamespace]) -> dict[str, Any]:
        outputs = {}
        for name, namespace in namespaces.items():
            if not isinstance(namespace, BaseNamespace):
                continue
            output = namespace.generate_metadata()
            if output is not None:
                outputs[name] = output
        return outputs