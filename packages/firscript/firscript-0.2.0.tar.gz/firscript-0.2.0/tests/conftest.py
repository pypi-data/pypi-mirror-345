import random
import pandas as pd
import pytest
import os

from firscript.namespaces.color import ColorNamespace 
from firscript.namespaces.chart import ChartNamespace
from firscript.namespaces.input import InputNamespace
from firscript.namespaces.strategy import StrategyNamespace
from firscript.namespaces.ta import TANamespace
from firscript.parser import ScriptParser
from firscript.script import ScriptType

@pytest.fixture
def parser():
    return ScriptParser()

@pytest.fixture
def runtime(request):
    return 

@pytest.fixture
def valid_strategy_script():
    return """
def setup():
    global fast_length, slow_length, trade_count, last_position
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)
    trade_count = 0
    last_position = None
    print(f"Strategy initialized with fast={fast_length}, slow={slow_length}")

def process():
    global trade_count, last_position
    fast_ma = ta.sma(data.all.close, fast_length)[-1]
    slow_ma = ta.sma(data.all.close, slow_length)[-1]
    close = data.current.close

    chart.plot(fast_ma, color=color.blue, title="Fast MA")
    chart.plot(slow_ma, color=color.red, title="Slow MA")

    if fast_ma > slow_ma and last_position != 'long':
        strategy.long()
        last_position = 'long'
        trade_count += 1
    elif fast_ma < slow_ma and last_position != 'short':
        strategy.short()
        last_position = 'short'
        trade_count += 1

    print(f"Close={close} | Fast MA={fast_ma} | Slow MA={slow_ma} | Trades={trade_count}")
"""

@pytest.fixture
def valid_indicator_script():
    return """
def calculate_sma(data, length = 14):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma
"""


@pytest.fixture
def sample_ohlcv_data():
    periods = 50  # Enough for all calculations
    data = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=periods),
        'close': [100 + 0.5*i + random.random() for i in range(periods)]
    })
    
    return data

@pytest.fixture
def multi_timeframe_strategy_script():
    return """
def setup():
    global fast_length, slow_length
    fast_length = input.int('Fast Length', 5)
    slow_length = input.int('Slow Length', 20)

def process():
    # Get higher timeframe data (simulated)
    higher_tf_data = {
        'close': [data.all.close[i] for i in range(0, len(data.all.close), 2)]
    }
    
    # Calculate indicators on both timeframes
    fast_ma = ta.sma(data.all.close, fast_length)[-1]
    slow_ma = ta.sma(higher_tf_data['close'], slow_length)[-1]
    
    if fast_ma > slow_ma:
        strategy.long()
    elif fast_ma < slow_ma:
        strategy.short()
"""

@pytest.fixture
def composite_indicator_script():
    return """
const sma = import 'sma_indicator'
const ema = import 'ema_indicator'

def calculate(data):
    sma_val = sma.calculate(data, 10)
    ema_val = ema.calculate(data, 10)
    return (sma_val + ema_val) / 2

export = calculate
"""