"""
Example demonstrating how to run a strategy script that imports a library script
"""
import random
import sys
import os
import pandas as pd

from firscript.engine import Engine
from firscript.script import Script, ScriptMetadata, ScriptType

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    # Create sample price data
    periods = 50
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })

    # Read the strategy script
    with open('examples/strategy_with_library_import.py', 'r') as f:
        strategy_script = f.read()
    
    # Read the library script that will be imported
    with open('examples/simple_library.py', 'r') as f:
        library_script = f.read()

    # Initialize engine with both scripts
    # The key in the dictionary is the script ID that will be used in import_script()
    engine = Engine(data, scripts=[
        Script(strategy_script, is_entrypoint=True, metadata=ScriptMetadata(id='main', name='main', type=ScriptType.STRATEGY)),
        Script(library_script, metadata=ScriptMetadata(id='simple_library', name='simple_library', type=ScriptType.LIBRARY))
    ])
    
    # Run the strategy
    result = engine.run()
    print("\nStrategy execution completed:")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
