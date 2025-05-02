"""
Test script for namespace output generation.
"""
from typing import Any
import pandas as pd
import pytest

from firscript.engine import Engine
from firscript.namespaces.base import BaseNamespace


def test_When_DefaultNamespacesRegistered_Expect_CanGenerateOutput():
    """Test that namespace outputs are generated correctly."""
    # Create test data
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=10),
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    })
    
    # Create a simple strategy script
    script_source = """
def setup():
    pass

def process():
    # Add a chart plot
    chart.plot(data.current.close, title="Close Price", color=color.blue)
    
    # Add a strategy order
    if data.current.close > 105:
        strategy.long()
    elif data.current.close < 102:
        strategy.short()
    """
    
    # Create the script engine with automatic output generation
    engine = Engine(
        data,
        main_script_str=script_source
    )
    
    # Run the script with data
    result = engine.run()[0]
    
    # Verify that we got namespace outputs
    assert isinstance(result, dict)
    assert "strategy" in result
    assert "chart" in result
    
    # Verify strategy output
    assert "position" in result["strategy"]
    assert "orders" in result["strategy"]
    
    # Verify chart output
    assert isinstance(result["chart"], list)
    assert len(result["chart"]) > 0
    assert "data" in result["chart"][0]
    assert "options" in result["chart"][0]

class CustomNamespace(BaseNamespace):
    """Custom namespace for testing."""
    
    def __init__(self, shared: dict[str, Any]):
        super().__init__(shared)
        self.value = 0
        
    def increment(self):
        """Increment the value."""
        self.value += 1
        
    def generate_output(self):
        """Generate output."""
        return {"value": self.value}
    
    def generate_metadata(self):
        """Generate metadata."""
        return {"metadata": "test"}


def test_When_RegisterCustomNamespace_Expect_CanGenerateMetadata():
    """Test that custom namespace outputs are generated correctly."""
    # Create test data
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=10),
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    })
    
    # Create a simple strategy script
    script_source = """
def setup():
    pass

def process():
    # Use custom namespace
    custom.increment()
    """
    
    # Create the script engine with automatic output generation
    engine = Engine(
        data,
        main_script_str=script_source,
    )
    
    # Register custom namespace
    engine.registry.register("custom", CustomNamespace(engine.registry.shared))
    
    # Run the script with data
    result, metadata = engine.run()
    
    # Verify that we got namespace outputs
    assert isinstance(metadata, dict)
    assert "custom" in metadata
    assert metadata["custom"]["metadata"] == "test"


def test_When_RegisterCustomNamespace_Expect_CanGenerateOutput():
    """Test that custom namespace outputs are generated correctly."""
    # Create test data
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=10),
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    })
    
    # Create a simple strategy script
    script_source = """
def setup():
    pass

def process():
    # Use custom namespace
    custom.increment()
    """
    
    # Create the script engine with automatic output generation
    engine = Engine(
        data,
        main_script_str=script_source,
    )
    
    # Register custom namespace
    engine.registry.register("custom", CustomNamespace(engine.registry.shared))
    
    # Run the script with data
    result = engine.run()[0]
    
    # Verify that we got namespace outputs
    assert isinstance(result, dict)
    assert "custom" in result
    assert result["custom"]["value"] == 10
