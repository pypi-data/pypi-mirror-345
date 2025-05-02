import pytest
from firscript.exceptions import NoExportsError, ReservedVariableNameError
from firscript.script import ScriptType

def test_library_with_reserved_variable_name_export(parser):
    """Test that a library script with a reserved variable name export raises an error."""
    invalid_library = """
__system_var__ = "This is a reserved variable name"

# Export a reserved variable name
export = __system_var__
"""
    with pytest.raises(ReservedVariableNameError):
        parser.parse(invalid_library, 'test_script_id', ScriptType.LIBRARY)

def test_library_with_reserved_variable_name_in_dict(parser):
    """Test that a library script with a reserved variable name in a dictionary export raises an error."""
    invalid_library = """
# Export a dictionary with a reserved variable name as a key
export = {
    "__system_key__": "This is a reserved key name",
    "normal_key": "This is fine"
}
"""
    with pytest.raises(ReservedVariableNameError):
        parser.parse(invalid_library, 'test_script_id', ScriptType.LIBRARY)

def test_library_with_reserved_export_name(parser):
    """Test that a library script with a reserved export name raises an error."""
    invalid_library = """
# Using a reserved name for the export variable itself
__export__ = "This is a reserved export name"
"""
    with pytest.raises(NoExportsError):
        parser.parse(invalid_library, 'test_script_id', ScriptType.LIBRARY)

def test_library_with_valid_variable_names(parser):
    """Test that a library script with valid variable names passes validation."""
    valid_library = """
normal_var = "This is a normal variable name"
_also_normal = "This is also normal"
CONSTANT_VAR = "This is a constant"

# Export with valid names
export = {
    "normal_key": normal_var,
    "another_key": _also_normal,
    "constant": CONSTANT_VAR
}
"""
    script = parser.parse(valid_library, 'test_script_id', ScriptType.LIBRARY)
    assert script is not None
