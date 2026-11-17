"""Dummy tool that proves the tool path works (job 1)."""
from datetime import datetime

SCHEMA = {
    "name": "get_time",
    "description": "Get the current local date and time.",
    "input_schema": {"type": "object", "properties": {}},
}


def run(tool_input: dict) -> str:
    return datetime.now().strftime("%A %Y-%m-%d %H:%M")
