"""Runtime-related exceptions for the script engine."""
from .base import ScriptEngineError

class ScriptRuntimeError(ScriptEngineError):
    """Raised when script execution fails."""
    def __init__(self, message, file=None, name=None, line_no=None, line_str=None, col_no=None, exception_msg=None):
        super().__init__(message)
        self.file = file
        self.name = name
        self.line_no = line_no
        self.line_str = line_str
        self.col_no = col_no
        self.exception_msg = exception_msg
        
class ScriptCompilationError(ScriptRuntimeError):
    """Raised when script compilation fails."""
    pass

class ScriptNotFoundError(ScriptRuntimeError):
    """Raised when a script definition cannot be found."""
    pass

class EntrypointNotFoundError(ScriptRuntimeError):
    """Raised when an entrypoint script cannot be found."""
    pass