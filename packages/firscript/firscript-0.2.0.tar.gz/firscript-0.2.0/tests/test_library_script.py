import pytest
from firscript.engine import Engine
from firscript.script import ScriptType
from firscript.exceptions import MissingScriptTypeError, ConflictingScriptTypeError, NoExportsError
import pandas as pd

def test_parse_valid_library_script(parser):
    """Test that a valid library script is parsed correctly."""
    library_script = """
def calculate_average(values):
    if not values:
        return 0
    return sum(values) / len(values)

def calculate_momentum(values, period=14):
    if len(values) < period:
        return 0
    return values[-1] - values[-period]

# Export the functions as a dictionary
export = {
    "average": calculate_average,
    "momentum": calculate_momentum
}
"""
    script = parser.parse(library_script, 'test_script_id', ScriptType.LIBRARY)
    assert script.metadata.type == ScriptType.LIBRARY

def test_When_LibraryScriptDefineSetupAndProcessFunction_Expect_NoError(parser):
    """Test that a library script with setup/process functions raises an error."""
    invalid_library = """
def setup():
    pass

def process():
    pass

export = {"function": lambda x: x}
"""
    parser.parse(invalid_library, 'test_script_id', ScriptType.LIBRARY)

def test_When_LibraryScriptNoDefineExport_Expect_NoExportsError(parser):
    """Test that a script without export and without setup/process raises an error."""
    invalid_script = """
def calculate_something():
    return 42
"""
    with pytest.raises(NoExportsError):
        parser.parse(invalid_script, 'test_script_id', ScriptType.LIBRARY)

# def test_When_LibraryScriptDefineMultipleExports_Expect_Error(parser):
#     """Test that a library script with multiple exports raises an error."""
#     invalid_library = """
# export = {"func1": lambda x: x}
# export = {"func2": lambda x: x * 2}
# """
#     with pytest.raises(Exception):  # Could be MultipleExportsError or similar
#         parser.parse(invalid_library, 'test_script_id', ScriptType.LIBRARY)

def test_When_EngineExecuteLibraryScript_Expect_ResultIsLibraryFunction(runtime, parser):
    """Test that a library script can be executed and returns the export value."""
    library_script = """
def calculate_average(values):
    if not values:
        return 0
    return sum(values) / len(values)

# Export a single function
export = calculate_average
"""
    # Create sample data
    data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104]
    })
    
    engine = Engine(
        data,
        main_script_str=library_script,
    )
    
    result, metadata = engine.run()
    # Verify that the result is the exported function
    assert result is not None
    assert callable(result)

    # Test the exported function
    test_values = [1, 2, 3, 4, 5]
    assert result(test_values) == 3.0  # Average of [1,2,3,4,5] is 3.0
