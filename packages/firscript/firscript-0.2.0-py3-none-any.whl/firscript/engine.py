from typing import Any
import pandas as pd
from firscript.exceptions.base import ScriptEngineError
from firscript.importer import ScriptImporter
from firscript.namespace_registry import NamespaceRegistry
from firscript.script import Script

class Engine:
    def __init__(self, data: pd.DataFrame, main_script_str: str = None, import_scripts: dict[str, str] = {}, scripts: list[Script] = None, inputs_override: dict[str, Any] = None,  column_mapping: dict[str, str] = None):
        self.main_script_str = main_script_str
        
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise ScriptEngineError("Input data must be a non-empty pandas DataFrame.")
        self.data = data
        
        self.registry = NamespaceRegistry()
        self.registry.register_default_namespaces(inputs_override, column_mapping=column_mapping)

        self.importer = ScriptImporter(self.registry)
        
        if scripts:
            for script in scripts:
                self.importer.add_script(script=script)
        else:
            self.importer.add_script('main', self.main_script_str, is_main=True)
            for name, script_str in import_scripts.items():
                self.importer.add_script(name, script_str)
        self.registry.register('import_script', self.importer.import_script)

    def run(self):
        ctx = self.importer.build_main_script()
        ctx.run_setup()
        
        metadatas = ctx.generate_metadatas()

        for i in range(len(self.data)):
            current_bar = self.data.iloc[i]  # Get current row as Series
            historical_bars = self.data.iloc[:i+1]  # Get all bars up to and including current row
            
            ctx.namespaces.get('data').set_current_bar(current_bar)
            ctx.namespaces.get('data').set_all_bar(historical_bars)
            ctx.run_process()
        
        export = ctx.get_export()
        result = ctx.generate_outputs()
        
        return export if export else result, metadatas


