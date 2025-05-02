from enum import Enum
from typing import override
import pandas as pd
import random
from firscript.engine import Engine
from firscript.importer import ScriptImporter
from firscript.namespace_registry import NamespaceRegistry
from firscript.namespaces.base import BaseNamespace
from firscript.parser import ScriptParser


# Define our own custom namespace
class CustomNamespace(BaseNamespace):
    def __init__(self):
        self.counter = 0

    def add_counter(self):
        self.counter += 1

    @override
    def generate_output(self):
        return {
            "output_text": "This is a custom output string.",
            "counter": self.counter,
        }


def main():
    # Create test data
    periods = 5
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-01-01", periods=periods),
            "close": [100 + 0.5 * i + random.random() for i in range(periods)],
        }
    )

    strategy_script = """
def setup():
    pass

def process():
    custom.add_counter()
"""

    # Prepare the runtime
    registry = NamespaceRegistry()
    registry.register("custom", CustomNamespace())
    registry.register_default_namespaces({})

    importer = ScriptImporter(registry)
    importer.add_script('main', strategy_script, is_main=True)    
        
    registry.register('import_script', importer.import_script)
    
    # Run the script
    ctx = importer.build_main_script()
    ctx.run_setup()
    
    print("=== Script Output ===")
    for i in range(len(data)):
        current_bar = data.iloc[i]  # Get current row as Series
        historical_bars = data.iloc[: i + 1]  # Get all bars up to and including current row
        registry.get("data").set_current_bar(current_bar)
        registry.get("data").set_all_bar(historical_bars)
        ctx.run_process()
        
    # Generate outputs
    result = ctx.generate_outputs()
    print(f"{result}")


main()
