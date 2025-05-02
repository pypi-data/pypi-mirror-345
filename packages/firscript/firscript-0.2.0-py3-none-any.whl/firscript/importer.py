from firscript.exceptions.parsing import CircularImportError
from firscript.exceptions.runtime import EntrypointNotFoundError, ScriptNotFoundError
from firscript.namespace_registry import NamespaceRegistry
from firscript.parser import ScriptParser
from firscript.script import Script
from firscript.execution_context import ScriptContext

class ScriptImporter:
    def __init__(self, registry: NamespaceRegistry):
        self.registry = registry
        self.loaded_scripts = {}
        self.import_stack = []
        self.scripts: dict[str, Script] = {}
        self.parser = ScriptParser()
        self.main_script: Script = None
        
    def add_script(self, name: str = None, script_str: str = None, is_main = False, script: Script = None) -> Script:
        if script is None:
            if name is None or script_str is None:
                raise ValueError("Either name and script_str or script must be provided.")
            result = self.parser.parse(script_str, name)
            self.scripts[name] = result
            if is_main:
                self.main_script = result
        else:
            result = self.parser.parse(script.source, script.id, script.type)
            self.scripts[script.id] = result
            if script.is_entrypoint:
                self.main_script = script
        return result
        
    def build_main_script(self) -> ScriptContext:
        if not self.main_script:
            raise EntrypointNotFoundError("No main script provided. Please provide the script through add_script")
        
        ctx =  ScriptContext(self.main_script.source, self.registry.build())
        ctx.compile()
        return ctx

    def import_script(self, name):
        if name in self.import_stack:
            # TODO: This is a very basic check for circular imports.
            # A more robust solution would be to use a graph data structure to track imports.
            raise CircularImportError(f"Cyclic import detected: {' → '.join(self.import_stack + [name])}")  # noqa: F821

        if name in self.loaded_scripts:
            return self.loaded_scripts[name]

        self.import_stack.append(name)
        try:
            if name not in self.scripts:
                raise ScriptNotFoundError(f"Script '{name}' not found.")
            script_str = self.scripts.get(name).source

            ctx = ScriptContext(script_str, self.registry.build(), name)
            ctx.compile()
            ctx.run_setup()
            self.loaded_scripts[name] = ctx
            
            export = ctx.get_export()
            return export if export else ctx
        finally:
            self.import_stack.pop()
