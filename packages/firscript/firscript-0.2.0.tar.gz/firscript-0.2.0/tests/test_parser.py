import pytest
from firscript.exceptions import MissingRequiredFunctionsError, MissingScriptTypeError, MultipleExportsError, NoExportsError, InvalidInputUsageError, StrategyFunctionInIndicatorError, ScriptParsingError
from firscript.script import ScriptType

def test_parse_valid_strategy(parser):
    script = parser.parse('''
def setup():
    length = input.int('Length', 10)
    return {'length': length}

def process():
    strategy.long()
    
''', 'test_script_id')
    assert script.metadata.type == ScriptType.STRATEGY

def test_parse_valid_indicator(parser):
    script = parser.parse('''
def setup():
    length = input.int('Length', 10)
    return {'length': length}

def process():
    pass
''', 'test_script_id')
    assert script.metadata.type == ScriptType.INDICATOR

def test_When_InputUsedInProcess_Expect_InvalidInputUsageError(parser):
    with pytest.raises(InvalidInputUsageError) as exc_info:
        parser.parse('''
def setup():
    global fast_length, slow_length
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)

def process():
    # Invalid: redefine inputs inside process, which should not happen
    fast_length = input.int('Fast MA Length', 10)
    slow_length = input.int('Slow MA Length', 20)
''', 'test_script_id')

def test_When_IndicatorInvalidFormat_Expect_MissingRequiredFunctionsError(parser):
    with pytest.raises(MissingRequiredFunctionsError) as exc_info:
        parser.parse('''
def setup():
    length = input.int('Length', 10)
''', 'test_script_id', ScriptType.INDICATOR)
        
def test_When_StrategyInvalidFormat_Expect_MissingRequiredFunctionsError(parser):
    with pytest.raises(MissingRequiredFunctionsError) as exc_info:
        parser.parse('''
def setup():
    length = input.int('Length', 10)
''', 'test_script_id', ScriptType.STRATEGY)

def test_parse_syntax_error(parser):
    invalid_syntax = """

"""
    with pytest.raises(ScriptParsingError) as exc_info:
        parser.parse(invalid_syntax, 'test_script_id')

def test_When_LibraryExportMissing_Expect_NoExportsError(parser):
    with pytest.raises(NoExportsError):
        parser.parse("""
def calculate():
    return 1
# Missing export statement
""", 'test_script_id', ScriptType.LIBRARY)

def test_When_StrategyImportIndicator_Expect_CorrectMetadataImports(parser):
    script_with_import = """
def setup():
    global indicator
    indicator = import_script('sma_indicator')

def process(bar):
    if indicator.sma_indicator > bar.close:
        strategy.long()
"""
    script = parser.parse(script_with_import, 'test_script_id')
    assert script.metadata.type == ScriptType.STRATEGY
    assert "sma_indicator" in script.metadata.imports.values()

def test_When_IndicatorUsesStrategyFunction_Expect_StrategyFunctionInIndicatorError(parser):
    invalid_indicator_with_strategy_call = """
def setup():
    global length
    length = input.int('Length', 14)

def process():
    sma_value = ta.sma(data.all.close, length)[-1]
    chart.plot(sma_value, color=color.blue, title="SMA")
    strategy.long()
"""
    with pytest.raises(StrategyFunctionInIndicatorError) as exc_info:
        parser.parse(invalid_indicator_with_strategy_call, 'test_script_id', ScriptType.INDICATOR)
        
def test_When_LibraryUsesStrategyFunction_Expect_StrategyFunctionInIndicatorError(parser):
    invalid_indicator_with_strategy_call = """
def calculate_sma(data, length):
    if len(data) < length:
        return None
    return sum(data[-length:]) / length

export = calculate_sma(bar.close, 14)

def dummy():
    strategy.long()
"""
    with pytest.raises(StrategyFunctionInIndicatorError) as exc_info:
        parser.parse(invalid_indicator_with_strategy_call, 'test_script_id', ScriptType.LIBRARY)
