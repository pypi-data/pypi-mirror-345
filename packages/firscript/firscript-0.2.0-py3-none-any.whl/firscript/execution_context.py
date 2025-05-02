import traceback
from types import SimpleNamespace
from typing import Any, Dict
from firscript.exceptions.runtime import ScriptCompilationError, ScriptRuntimeError
from firscript.namespace_registry import NamespaceRegistry
from firscript.namespaces.base import BaseNamespace


class ScriptContext:
    def __init__(
        self, script_str: str, namespaces: dict[str, BaseNamespace], name="<script>"
    ):
        self.name = name
        self.script_str = script_str
        self.namespaces = namespaces
        self.locals = {}
        self.globals = {}
        self._prepare_global_context()

    def compile(self):
        try:
            code = compile(self.script_str, self.name, "exec")
            exec(code, self.globals, self.locals)
        except Exception as e:
            raise ScriptCompilationError(f"Error compiling script: {e}")

    def run_setup(self):
        try:
            if "setup" in self.locals:
                self.locals["setup"]()
        except Exception as e:
            # Extract the last traceback entry with useful info
            last_tb = traceback.extract_tb(e.__traceback__)[-1]
            raise ScriptRuntimeError(f"Error in setup function: {e}", 
                                     file=self.name, 
                                     exception_msg=str(e),
                                     line_no=last_tb.lineno,
                                     line_str=last_tb.line,
                                     col_no=last_tb.colno)

    def run_process(self):
        try:
            if "process" in self.locals:
                return self.locals["process"]()
        except Exception as e:
            # Extract the last traceback entry with useful info
            last_tb = traceback.extract_tb(e.__traceback__)[-1]
            raise ScriptRuntimeError(f"Error in process function: {e}", 
                                     file=self.name, 
                                     exception_msg=str(e),
                                     line_no=last_tb.lineno,
                                     line_str=last_tb.line,
                                     col_no=last_tb.colno)
        
    def get_export(self):
        try:
            export_value = self.locals.get('export', None)
            # If export is a dictionary, convert it to SimpleNamespace for dot notation
            if isinstance(export_value, dict):
                return SimpleNamespace(**export_value)
            return export_value
        except Exception as e:
            # Extract the last traceback entry with useful info
            last_tb = traceback.extract_tb(e.__traceback__)[-1]
            raise ScriptRuntimeError(f"Error in export: {e}", 
                                     file=self.name, 
                                     exception_msg=str(e),
                                     line_no=last_tb.lineno,
                                     line_str=last_tb.line,
                                     col_no=last_tb.colno)

    def generate_outputs(self) -> Dict[str, Any]:
        """
        Generate outputs from all namespaces that support output generation.

        Returns:
            A dictionary mapping namespace names to their generated outputs.
        """
        return NamespaceRegistry.generate_outputs(self.namespaces)
    
    def generate_metadatas(self) -> Dict[str, Any]:
        """
        Generate metadata outputs from all namespaces that support metadata generation.

        Returns:
            A dictionary mapping namespace names to their generated metadatas.
        """
        return NamespaceRegistry.generate_metadatas(self.namespaces)
    
    def _prepare_global_context(self):
        """Initialize the execution context with safe builtins."""
        # Basic builtins, can be customized further
        self.globals['__builtins__'] = {
            'print': print,
            'len': len,
            'range': range,
            'abs': abs,
            'round': round,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'sum': sum,
            'max': max,
            'min': min,
            'type': type
            # Add other safe builtins as needed
        }
        # Prevent access to potentially harmful builtins
        self.globals['__builtins__']['eval'] = None
        self.globals['__builtins__']['exec'] = None
        self.globals['__builtins__']['open'] = None
        self.globals['__builtins__']['compile'] = None
        self.globals['__builtins__']['input'] = None
        self.globals['__builtins__']['__import__'] = None
        # Inject standard namespaces
        self.globals.update(self.namespaces)
