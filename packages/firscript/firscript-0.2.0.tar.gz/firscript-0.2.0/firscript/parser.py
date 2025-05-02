import ast
import re
from typing import Any, Dict, List, Set, Tuple

from firscript.exceptions import StrategyGlobalVariableError, ReservedVariableNameError
from firscript.exceptions.parsing import ConflictingScriptTypeError, InvalidInputUsageError, MissingRequiredFunctionsError, MissingScriptTypeError, MultipleExportsError, NoExportsError, StrategyFunctionInIndicatorError
from .script import Script, ScriptType, ScriptMetadata

class ScriptParser:
    def __init__(self):
        self.required_strategy_functions = {"setup", "process"}
        self.reserved_var_pattern = re.compile(r'^__.*__$')  # Pattern for reserved variable names

    def parse(self, source: str, script_id: str, script_type: ScriptType = None) -> Script:
        """Parse and validate a script source."""
        try:
            tree = ast.parse(source)
            
            if script_type is None:
                script_type = self._determine_script_type(tree)

            # Extract metadata
            metadata = self._extract_metadata(tree, script_type, script_id)
            
            # Validate script constraints
            self._validate_script(tree, metadata)

            # Create script instance
            return self._create_script(source, metadata)

        except SyntaxError as e:
            from firscript.exceptions.parsing import ScriptParsingError
            raise ScriptParsingError(f"Invalid script syntax: {str(e)}")

    def _determine_script_type(self, tree: ast.AST) -> ScriptType:
        """Determine the script type based on function definitions and exports.

        A script is considered a:
        - Strategy: if it contains both setup() and process() functions without export.
        - Indicator: if it contains both setup() and process() functions (same as strategy).
        - Library: if it has an export variable but no setup/process functions.

        Raises:
            ConflictingScriptTypeError: If script has conflicting characteristics
            MissingScriptTypeError: If script doesn't match any type criteria
        """
        has_setup = False
        has_process = False
        has_export = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == "setup":
                    has_setup = True
                elif node.name == "process":
                    has_process = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "export":
                        has_export = True

        is_strategy_or_indicator = has_setup and has_process
        is_library = has_export and not (has_setup and has_process)

        # Determine script type based on characteristics
        if is_strategy_or_indicator and has_export:
            raise ConflictingScriptTypeError(
                "Script cannot have both setup/process functions and an export variable at the module level"
            )
        elif is_strategy_or_indicator:
            # Check for strategy namespace usage to differentiate between strategy and indicator
            uses_strategy_namespace = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "strategy":
                        uses_strategy_namespace = True
                        break

            if uses_strategy_namespace:
                return ScriptType.STRATEGY
            else:
                return ScriptType.INDICATOR
        elif is_library:
            return ScriptType.LIBRARY
        else:
            raise MissingScriptTypeError(
                "Script must be either a strategy/indicator (with setup/process functions) or a library (with export variable)"
            )

    def _extract_metadata(self, tree: ast.AST, script_type: ScriptType, script_id: str) -> ScriptMetadata:
        """Extract metadata from the script."""
        exports = set()
        # Dictionary to store custom imports: {alias: definition_id}
        custom_imports: Dict[str, str] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Detect custom import assignments like: my_sma = import_script('indicators/sma.py')
                if isinstance(node.value, ast.Call) and \
                   isinstance(node.value.func, ast.Name) and \
                   node.value.func.id == 'import_script' and \
                   len(node.targets) == 1 and \
                   isinstance(node.targets[0], ast.Name) and \
                   len(node.value.args) == 1 and \
                   isinstance(node.value.args[0], ast.Constant) and \
                   isinstance(node.value.args[0].value, str):

                    alias = node.targets[0].id
                    definition_id = node.value.args[0].value
                    if alias in custom_imports:
                         # Handle potential duplicate aliases if needed (e.g., raise error or log warning)
                         # Using logger requires importing logging
                         # logger.warning(f"Duplicate import alias '{alias}' detected. Overwriting previous import.")
                         pass # Or raise an error
                    custom_imports[alias] = definition_id
                # Detect export assignments
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("export"):
                        # Check if any variable with reserved name pattern is being exported
                        if target.id == "export" and isinstance(node.value, ast.Name) and self._is_reserved_variable_name(node.value.id):
                            raise ReservedVariableNameError(f"Cannot export variable with reserved name pattern: {node.value.id}")
                        # Check if the export variable itself has a reserved name pattern
                        if self._is_reserved_variable_name(target.id):
                            raise ReservedVariableNameError(f"Cannot use reserved name pattern for export variable: {target.id}")
                        exports.add(target.id)

        return ScriptMetadata(
            id=script_id,
            name=script_id,
            type=script_type,
            exports=exports,
            imports=custom_imports # Use the correct variable name
        )

    def _validate_script(self, tree: ast.AST, metadata: ScriptMetadata) -> None:
        """Validate script against all constraints."""
        if metadata.type == ScriptType.STRATEGY:
            self._validate_strategy_script(tree)
        elif metadata.type == ScriptType.INDICATOR:
            self._validate_indicator_script(tree)
        elif metadata.type == ScriptType.LIBRARY:
            self._validate_library_script(tree)
        else:
            # This should never happen as _determine_script_type should catch invalid types
            raise ValueError(f"Unknown script type: {metadata.type}")

    def _validate_strategy_script(self, tree: ast.AST) -> None:
        """Validate strategy script constraints."""
        # Check for required functions
        functions = {node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)}
        missing = self.required_strategy_functions - functions
        if missing:
            raise MissingRequiredFunctionsError(f"Strategy script missing required functions: {missing}")

        # Check for input usage in process function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "process":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if isinstance(child.func.value, ast.Name) and child.func.value.id == "input":
                                raise InvalidInputUsageError("Input functions cannot be used inside process()")

        # Check for variable assignments at module level (outside setup & process)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        raise StrategyGlobalVariableError(f"Variable '{var_name}' assigned at global scope. Move all variable declarations inside setup() or process().")

    def _validate_indicator_script(self, tree: ast.AST) -> None:
        """Validate indicator script constraints."""
        # Check for required functions (same as strategy)
        functions = {node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)}
        missing = self.required_strategy_functions - functions
        if missing:
            raise MissingRequiredFunctionsError(f"Indicator script missing required functions: {missing}")

        # Check for strategy function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "strategy":
                        raise StrategyFunctionInIndicatorError("Indicator scripts cannot use strategy functions")
        
        # Check for input usage in process function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "process":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if isinstance(child.func.value, ast.Name) and child.func.value.id == "input":
                                raise InvalidInputUsageError("Input functions cannot be used inside process()")

        # Check for variable assignments at module level (outside setup & process)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        raise StrategyGlobalVariableError(f"Variable '{var_name}' assigned at global scope. Move all variable declarations inside setup() or process().")

    def _validate_library_script(self, tree: ast.AST) -> None:
        """Validate library script constraints."""
        # Check for single export
        exports = {node.targets[0].id for node in ast.walk(tree)
                  if isinstance(node, ast.Assign)
                  and isinstance(node.targets[0], ast.Name)
                  and node.targets[0].id == 'export'}
        if len(exports) > 1:
            raise MultipleExportsError("Library script must have exactly one export")
        elif len(exports) < 1:
            raise NoExportsError("Library script must have at least one export")

        # Check for reserved variable names in dictionary exports
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'export':
                # Check if export is a dictionary
                if isinstance(node.value, ast.Dict):
                    # Check dictionary keys for reserved names
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str) and self._is_reserved_variable_name(key.value):
                            raise ReservedVariableNameError(f"Cannot use reserved name pattern in export dictionary key: {key.value}")

        # Check for strategy function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "strategy":
                        raise StrategyFunctionInIndicatorError("Library scripts cannot use strategy functions")

    def _is_reserved_variable_name(self, var_name: str) -> bool:
        """Check if a variable name matches the reserved pattern (__name__)."""
        return bool(self.reserved_var_pattern.match(var_name))

    def _create_script(self, source: str, metadata: ScriptMetadata) -> Script:
        """Create script instance with source and metadata."""
        return Script(source, metadata)