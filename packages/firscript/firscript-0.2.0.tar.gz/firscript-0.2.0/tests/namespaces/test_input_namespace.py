from typing import Any, override
import pandas as pd

from firscript.engine import Engine
from firscript.namespaces.base import BaseNamespace


def test_When_CreateInputInSetup_Expect_ShowInputInMetadata():
    script = """
def setup():
    input.int("Length", 10)
    input.text("Name", "John")
    input.float("Price", 100.0)
    input.bool("Active", True)

def process():
    pass
"""
    
    engine = Engine(pd.DataFrame({"timestamp": pd.date_range("2023-01-01", periods=10), "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}), main_script_str=script)
    result, metadata = engine.run()
    assert len(metadata["input"]) == 4
    assert "Length" in metadata["input"]
    assert metadata["input"]["Length"].default == 10
    assert metadata["input"]["Length"].type == "int"
    assert "Name" in metadata["input"]
    assert metadata["input"]["Name"].default == "John"
    assert metadata["input"]["Name"].type == "text"
    assert "Price" in metadata["input"]
    assert metadata["input"]["Price"].default == 100.0
    assert metadata["input"]["Price"].type == "float"
    assert "Active" in metadata["input"]
    assert metadata["input"]["Active"].default == True
    assert metadata["input"]["Active"].type == "bool"

def test_When_EngineOverrideInput_Expect_ShowValueOverrideInProcess():
    script = """
def setup():
    global length
    length = input.int("Length", 10)

def process():
    log.info(f"Length: {length}")
"""
    engine = Engine(pd.DataFrame({"timestamp": pd.date_range("2023-01-01", periods=10), "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}), main_script_str=script, inputs_override={"Length": 20})
    result, metadata = engine.run()
    assert len(result["log"]["info"]) == 10
    assert result["log"]["info"].pop() == "Length: 20"
