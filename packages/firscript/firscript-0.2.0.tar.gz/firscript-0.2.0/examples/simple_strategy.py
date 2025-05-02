"""
MA Crossover Strategy
Demonstrates state persistence and basic moving average crossover logic
"""

def setup():
    """Initialize strategy state"""
    global trade_count, last_position, fast_length, slow_length
    fast_length = input.int('Fast MA Length', 5)
    slow_length = input.int('Slow MA Length', 10)
    trade_count = 0
    last_position = None
    print(f"Strategy initialized with fast={fast_length}, slow={slow_length}")

def process():
    """Process each bar"""
    global trade_count, last_position
    
    # Get indicator values
    fast_ma = ta.sma(data.all.close, fast_length)
    slow_ma = ta.sma(data.all.close, slow_length)
    close = data.current.close
    
    # Plot the moving averages
    chart.plot(fast_ma[-1], color=color.blue, title="Fast MA")
    chart.plot(slow_ma[-1], color=color.red, title="Slow MA")
    
    # Trading logic - MA crossover
    if ta.crossover(fast_ma,slow_ma):
        strategy.long()
        last_position = 'long'
        trade_count += 1
    elif ta.crossunder(fast_ma,slow_ma):
        strategy.short()
        last_position = 'short'
        trade_count += 1
        
    # Debug output
    fast_ma_str = f'{fast_ma[-1]:.2f}' if fast_ma[-1] is not None else f'{fast_ma[-1]}'
    slow_ma_str = f'{slow_ma[-1]:.2f}' if slow_ma[-1] is not None else f'{slow_ma[-1]}'
    print(f"{data.current.timestamp}: Close={close:.2f} | Fast MA={fast_ma_str} | Slow MA={slow_ma_str} | Trades={trade_count}")