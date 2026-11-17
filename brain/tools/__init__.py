"""Tool registry. One file per tool; each exports SCHEMA (what Claude sees) and run(input) -> str."""
from . import clock

_TOOLS = {m.SCHEMA["name"]: m for m in (clock,)}

TOOL_SCHEMAS = [m.SCHEMA for m in _TOOLS.values()]


def run_tool(name: str, tool_input: dict) -> str:
    # Tool output is DATA for the model. It never triggers an action by itself.
    if name not in _TOOLS:
        return f"error: unknown tool {name}"
    try:
        return _TOOLS[name].run(tool_input)
    except Exception as e:  # a broken tool must not kill the loop
        return f"error: {e}"
