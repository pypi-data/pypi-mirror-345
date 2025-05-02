# import pytest
# import pandas as pd
# from firscript.exceptions import MissingScriptTypeError, StrategyGlobalVariableError
# from firscript.exceptions.runtime import ScriptRuntimeError, ScriptCompilationError
# from firscript.script import ScriptType


# def test_When_ExecuteValidIndicatorScript_Expect_ResultReturned(
#     runtime, parser, valid_indicator_script, sample_ohlcv_data
# ):
#     script = parser.parse(valid_indicator_script)
#     result = runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#         ),
#     )
#     assert result is not None  # Placeholder implementation returns 0.0


# def test_When_ImportIndicator_Expect_CorrectImportOrError(runtime, parser):
#     # First register an indicator
#     indicator_script = """
# def calculate_sma(data, length = 14):
#     return sum(data[-length:]) / length

# export = calculate_sma
# """
#     indicator = parser.parse(indicator_script)
#     runtime.imported_indicators["sma_indicator"] = indicator

#     # Test importing the indicator
#     result = runtime._import_indicator("sma_indicator")
#     assert result == indicator

#     # Test importing non-existent indicator
#     with pytest.raises(ValueError) as exc_info:
#         runtime._import_indicator("non_existent")
#     assert "Indicator 'non_existent' not found" in str(exc_info.value)


# def test_When_RuntimeInitialized_Expect_AllNamespacesInjected(runtime):
#     # Test TA namespace
#     assert callable(runtime.registered_namespaces["ta"].ema)
#     assert callable(runtime.registered_namespaces["ta"].rsi)

#     # Test input namespace
#     assert callable(runtime.registered_namespaces["input"].int)
#     assert callable(runtime.registered_namespaces["input"].float)
#     assert callable(runtime.registered_namespaces["input"].text)

#     # Test chart namespace
#     assert callable(runtime.registered_namespaces["chart"].plot)

#     # Test color namespace (likely constants)
#     assert runtime.registered_namespaces["color"].red is not None
#     assert runtime.registered_namespaces["color"].green is not None
#     assert runtime.registered_namespaces["color"].blue is not None

#     # Test strategy namespace
#     assert callable(runtime.registered_namespaces["strategy"].long)
#     assert callable(runtime.registered_namespaces["strategy"].short)


# def test_When_InputDefaultValuesProvided_Expect_CorrectInjection(runtime, parser):
#     script = parser.parse("""
# def setup():
#     global length
#     length = input.int('Length', 10)

# def process():
#     pass
# """)
#     # Execute with input override
#     runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=pd.Series(), all_bar=pd.DataFrame()
#         ),
#     )
#     assert runtime.shared_context["length"] == 10


# @pytest.mark.parametrize(
#     "runtime", [{"inputs_override": {"Length": "Invalid"}}], indirect=True
# )
# def test_When_InvalidInputType_Expect_TypeError(runtime, parser):
#     script = parser.parse("""
# def setup():
#     global length
#     length = input.int('Length', 10)

# def process():
#     pass
# """)
#     with pytest.raises(ScriptRuntimeError):
#         runtime.execute_script(
#             script,
#             execution_input=ExecutionInputBase(
#                 current_bar=pd.Series(), all_bar=pd.DataFrame()
#             ),
#         )


# def test_When_MissingRequiredInput_Expect_ScriptRuntimeError(runtime, parser):
#     script = parser.parse("""
# def setup():
#     global length
#     length = input.int('Length')

# def process():
#     pass
# """)
#     with pytest.raises(ScriptRuntimeError):
#         runtime.execute_script(
#             script,
#             execution_input=ExecutionInputBase(
#                 current_bar=pd.Series(), all_bar=pd.DataFrame()
#             ),
#         )


# def test_When_NestedIndicatorImports_Expect_CorrectExecution(
#     runtime, parser, composite_indicator_script
# ):
#     # Register required indicators
#     sma_script = parser.parse("""
# def calculate(data, length):
#     return sum(data[-length:]) / length
# export = calculate
# """)
#     ema_script = parser.parse("""
# def calculate(data, length):
#     return sum(data[-length:]) / length  # Simplified for test
# export = calculate
# """)
#     runtime.imported_indicators["sma_indicator"] = sma_script
#     runtime.imported_indicators["ema_indicator"] = ema_script

#     # Test composite indicator
#     script = parser.parse(composite_indicator_script)
#     result = runtime.execute_script(script)
#     assert callable(result)


# def test_When_MultiTimeframeStrategy_Expect_ProperBarHandling(
#     runtime, parser, multi_timeframe_strategy_script, sample_ohlcv_data
# ):
#     pass
#     # script = parser.parse(multi_timeframe_strategy_script)
#     # process_func = runtime.execute_script(
#     #     script,
#     #     execution_input=ExecutionInputBase(
#     #         current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#     #     ),
#     # )
#     # process_func()  # Should execute without errors


# def test_When_LargeDataSet_Expect_ReasonableExecutionTime(
#     runtime, parser, benchmark, valid_strategy_script
# ):
#     # Create large dataset
#     large_data = pd.DataFrame({"close": [100 + 0.1 * i for i in range(10000)]})

#     script = parser.parse(valid_strategy_script)

#     def execute():
#         process_func = runtime.execute_script(
#             script,
#             execution_input=ExecutionInputBase(
#                 current_bar=large_data.iloc[-1], all_bar=large_data
#             ),
#         )
#         process_func()

#     # Benchmark execution
#     benchmark(execute)
#     assert benchmark.stats["mean"] < 0.1  # Should execute in <100ms


# def test_When_MultipleIndicatorImports_Expect_ProperCaching(runtime, parser, benchmark):
#     # Create simple indicator
#     indicator_script = """
# def calculate(data):
#     return sum(data) / len(data)
# export = calculate
# """
#     script = parser.parse(indicator_script)
#     runtime.imported_indicators["test_indicator"] = script

#     # Test import performance
#     def import_indicator():
#         runtime._import_indicator("test_indicator")

#     first_run = benchmark(import_indicator)
#     second_run = benchmark(import_indicator)

#     # Second run should be significantly faster due to caching
#     assert second_run.stats["mean"] < first_run.stats["mean"] * 0.5


# def test_When_CompositeIndicator_Expect_CorrectCalculation(
#     runtime, parser, composite_indicator_script, sample_ohlcv_data
# ):
#     # Setup indicators
#     sma_script = parser.parse("""
# def calculate(data, length):
#     return sum(data[-length:]) / length
# export = calculate
# """)
#     ema_script = parser.parse("""
# def calculate(data, length):
#     return sum(data[-length:]) / length  # Simplified for test
# export = calculate
# """)
#     runtime.imported_indicators["sma_indicator"] = sma_script
#     runtime.imported_indicators["ema_indicator"] = ema_script

#     # Test composite indicator
#     script = parser.parse(composite_indicator_script)
#     calculate = runtime.execute_script(script)
#     result = calculate(sample_ohlcv_data["close"].tolist())
#     assert result is not None


# def test_When_StrategyWithRiskManagement_Expect_PositionUpdates(
#     runtime, parser, risk_management_strategy_script, sample_ohlcv_data
# ):
#     script = parser.parse(risk_management_strategy_script)
#     process_func = runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#         ),
#     )
#     process_func()  # Should execute without errors


# @pytest.mark.parametrize(
#     "runtime", [{"inputs_override": {"Length": 20}}], indirect=True
# )
# def test_When_OverrideDefaultInput_Expect_CorrectValueUsed(runtime, parser):
#     script = parser.parse("""
# def setup():
#     global length
#     length = input.int('Length', 10)

# def process():
#     pass
# """)
#     runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=pd.Series(), all_bar=pd.DataFrame()
#         ),
#     )
#     assert runtime.shared_context["length"] == 20


# def test_When_ExecuteMultipleProcessCalls_Expect_StatePersisted(
#     runtime, parser, sample_ohlcv_data
# ):
#     script = parser.parse("""
# def setup():
#     global trade_count
#     trade_count = 0

# def process():
#     global trade_count
#     trade_count += 1
# """)

#     # First call - should initialize state
#     runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#         ),
#     )
#     assert runtime.shared_context["trade_count"] == 1

#     # Second call - state should persist
#     runtime.execute_script(
#         script,
#         execution_input=ExecutionInputBase(
#             current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#         ),
#     )
#     assert (
#         runtime.shared_context["trade_count"] >= 2
#     )  # Could be 0 or 1 depending on conditions


# def test_When_GlobalMutableStateDetected_Expect_WarningLogged(
#     runtime, parser, sample_ohlcv_data, caplog
# ):
#     script_with_global_state = """
# global_var = 0  # Global mutable state

# def setup():
#     pass

# def process():
#     global global_var
#     global_var += 1
# """
#     with pytest.raises(StrategyGlobalVariableError):
#         script = parser.parse(script_with_global_state)
#         runtime.execute_script(
#             script,
#             execution_input=ExecutionInputBase(
#                 current_bar=sample_ohlcv_data.iloc[-1], all_bar=sample_ohlcv_data
#             ),
#         )


# def test_When_UndefinedVariableUsed_Expect_ScriptRuntimeError(runtime, parser):
#     script = parser.parse("""
# def setup():
#     pass

# def process():
#     undefined_var += 1  # Undefined variable
# """)
#     with pytest.raises(ScriptRuntimeError):
#         runtime.execute_script(
#             script,
#             execution_input=ExecutionInputBase(
#                 current_bar=pd.Series(), all_bar=pd.DataFrame()
#             ),
#         )


# def test_When_ImportCycleDetected_Expect_RecursionError(runtime, parser):
#     # Create two indicators that import each other
#     indicator1 = parser.parse("""
# const ind2 = import 'indicator2'
# def calculate():
#     return ind2.calculate() + 1
# export = calculate
# """)
#     indicator2 = parser.parse("""
# const ind1 = import 'indicator1'
# def calculate():
#     return ind1.calculate() + 1
# export = calculate
# """)

#     runtime.imported_indicators["indicator1"] = indicator1
#     runtime.imported_indicators["indicator2"] = indicator2

#     with pytest.raises(RecursionError):
#         runtime._import_indicator("indicator1")
