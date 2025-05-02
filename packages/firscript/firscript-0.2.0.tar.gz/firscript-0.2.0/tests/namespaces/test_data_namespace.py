from typing import Any, override
import pandas as pd

from firscript.engine import Engine
from firscript.namespaces.base import BaseNamespace


def test_When_AccessCloseVariable_Expect_ShowCurrentClose():
    script = """
def setup():
    pass

def process():
    log.info(f"Close: {data.close}")
"""
    
    engine = Engine(pd.DataFrame({"timestamp": pd.date_range("2023-01-01", periods=10), "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}), main_script_str=script)
    result, metadata = engine.run()
    assert len(result["log"]["info"]) == 10
    assert result["log"]["info"].pop() == "Close: 109"
    
def test_When_AccessHistoricalCloseVariable_Expect_ShowSecondLastClose():
    script = """
def setup():
    pass

def process():
    log.info(f"Close: {data.close[1]}")
"""
    
    engine = Engine(pd.DataFrame({"timestamp": pd.date_range("2023-01-01", periods=10), "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}), main_script_str=script)
    result, metadata = engine.run()
    assert len(result["log"]["info"]) == 10
    assert result["log"]["info"].pop() == "Close: 108"