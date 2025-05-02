"""
Simple example demonstrating how to run a strategy script
"""
import random
import pandas as pd
from firscript.engine import Engine

def main():
    # Create sample price data
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=20),
        'close': [
            100, 102, 104, 105, 103,  # Uptrend
            101, 98, 96, 95, 94,      # Downtrend
            93, 95, 98, 100, 102,     # Uptrend again
            101, 98, 97, 95, 93       # Final downtrend
        ]
    })

    # Read the strategy script
    with open('examples/simple_strategy.py', 'r') as f:
        strategy_script = f.read()

    # Initialize engine
    engine = Engine(data, main_script_str=strategy_script)
    
    # Run the strategy
    result = engine.run()
    print("\nStrategy execution completed:")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
