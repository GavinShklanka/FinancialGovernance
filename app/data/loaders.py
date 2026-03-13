"""
Antigravity — JSON loader utility.
"""

import json
import os


def load_json(path: str) -> dict:
    """Read and parse a JSON file, resolving relative paths from the project root."""
    # Resolve relative paths from the project root (two levels up from app/data/)
    if not os.path.isabs(path):
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        path = os.path.join(project_root, path)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
