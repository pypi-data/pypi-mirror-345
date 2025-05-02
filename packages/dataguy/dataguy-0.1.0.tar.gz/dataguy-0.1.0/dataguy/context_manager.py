# context_manager.py

import builtins
import types
import pandas as pd
import numpy as np

class ContextManager:
    """
    Tracks a concise Python execution context for LLM prompts:
      - Non-private module imports
      - Relevant variables (DataFrames, arrays, primitives, lists, dicts)
      - Recent executed code history
    """

    def __init__(self, max_code_history=100):
        self.imported_packages = set()
        self.variables = {}
        self.code_history = []
        self.max_code_history = max_code_history

    def update_from_globals(self, globals_dict):
        """
        Rebuilds the context from the given globals dictionary,
        keeping only non-private modules and meaningful variables.
        """
        # Reset previous context
        self.imported_packages.clear()
        self.variables.clear()

        # 1) Track non-private module imports
        for name, obj in globals_dict.items():
            if isinstance(obj, types.ModuleType) and not name.startswith('_'):
                self.imported_packages.add(name)

        # 2) Track only “interesting” variables
        for name, obj in globals_dict.items():
            # Skip private names, builtins, modules, and callables
            if (
                name.startswith('_') or
                name in builtins.__dict__ or
                isinstance(obj, types.ModuleType) or
                callable(obj)
            ):
                continue

            # Keep DataFrame, ndarray, list, dict, primitives
            if isinstance(obj, (pd.DataFrame, np.ndarray, list, dict, int, float, str, bool)):
                t = type(obj).__name__
                # Show shape for arrays/DataFrames
                if hasattr(obj, 'shape'):
                    self.variables[name] = f"{t}{obj.shape}"
                else:
                    self.variables[name] = t

    def add_code(self, code: str):
        """
        Appends executed code lines to history (up to max length).
        """
        lines = code.strip().split('\n')
        self.code_history.extend(lines)
        if len(self.code_history) > self.max_code_history:
            self.code_history = self.code_history[-self.max_code_history:]

    def get_context_summary(self) -> str:
        """
        Returns a markdown-like summary:
          - Imports
          - Variables
          - Recent code history
        """
        lines = ["# CONTEXT", ""]
        # Imports
        lines.append("## Imports")
        lines.append(", ".join(sorted(self.imported_packages)) or "None")
        # Variables
        lines.append("\n## Variables")
        if self.variables:
            for k, v in sorted(self.variables.items()):
                lines.append(f"- {k}: {v}")
        else:
            lines.append("None")
        # Code history
        lines.append("\n## Code History")
        if self.code_history:
            lines.append("```python")
            lines.extend(self.code_history)
            lines.append("```")
        else:
            lines.append("None")

        return "\n".join(lines)
