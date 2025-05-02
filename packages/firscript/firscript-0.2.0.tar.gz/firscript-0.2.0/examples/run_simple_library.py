"""
Simple example demonstrating how to run a library script
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

    # Read the library script
    with open('examples/simple_library.py', 'r') as f:
        library_script = f.read()

    # Initialize engine
    engine = Engine(data, main_script_str=library_script)
    
    # Run the library
    lib = engine.run()
    
    # Use the exported functions
    close_prices = data['close'].tolist()
    avg = lib[0].average(close_prices)
    momentum = lib[0].momentum(close_prices)
    roc = lib[0].roc(close_prices)
    
    print("\nLibrary execution completed:")
    print(f"Average: {avg:.2f}")
    print(f"Momentum: {momentum:.2f}")
    print(f"Rate of Change: {roc:.2f}%")

if __name__ == "__main__":
    main()