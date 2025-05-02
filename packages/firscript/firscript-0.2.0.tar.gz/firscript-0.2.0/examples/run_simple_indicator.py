"""
Simple example demonstrating how to run an indicator script
"""
import random
import pandas as pd
from firscript.engine import Engine

def main():
    # Create sample price data
    periods = 50
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })

    # Read the indicator script
    with open('examples/simple_indicator.py', 'r') as f:
        indicator_script = f.read()

    # Initialize engine
    engine = Engine(data, main_script_str=indicator_script)
    
    # Run the indicator
    result = engine.run()
    print("\nIndicator execution completed:")
    print(f"Final SMA value: {result}")

if __name__ == "__main__":
    main()