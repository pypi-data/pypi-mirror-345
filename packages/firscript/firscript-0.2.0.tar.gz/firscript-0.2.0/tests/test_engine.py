from typing import Any, override
import pandas as pd

from firscript.engine import Engine
from firscript.namespaces.base import BaseNamespace


def test_When_EngineInitialized_Expect_CanRegisterNewNamespace():
    class CustomNamespace(BaseNamespace):
        """Custom namespace for testing."""
        def __init__(self, shared: dict[str, Any]):
            super().__init__(shared)
            self.text = ""
            
        def custom_function(self):
            self.text = "Hello, World!"
        
        @override
        def generate_output(self):
            return {"custom_output": self.text}
        
    script = """
def setup():
    pass

def process():
    custom.custom_function()
"""
    
    engine = Engine(pd.DataFrame({"timestamp": pd.date_range("2023-01-01", periods=10)}), main_script_str=script)
    engine.registry.register("custom", CustomNamespace(engine.registry.shared))
    result, metadata = engine.run()
    assert "custom" in engine.registry.namespaces
    assert result["custom"]["custom_output"] == "Hello, World!"