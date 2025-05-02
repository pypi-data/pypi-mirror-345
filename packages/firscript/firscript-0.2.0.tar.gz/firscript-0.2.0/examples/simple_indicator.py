"""
Simple Moving Average Indicator (New Format)
Calculates SMA of closing prices for given length
"""

def setup():
    """Initialize indicator parameters"""
    global length
    length = input.int('Length', 14)
    print(f"Indicator initialized with length={length}")

def process():
    """Process each bar"""
    # Calculate SMA using current bar's close price
    sma_value = ta.sma(data.all.close, length)[-1]
    
    # Plot the SMA
    chart.plot(sma_value, color=color.blue, title="SMA")
    
    # Print debug info
    sma_str = f'{sma_value:.2f}' if sma_value is not None else f'{sma_value}'
    print(f"{data.current.timestamp}: Close={data.current.close:.2f} | SMA={sma_str}")
