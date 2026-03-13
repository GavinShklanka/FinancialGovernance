"""
Antigravity — Atomic Writer
Writes JSON files safely using temporary files and atomic OS replacement.
"""

import json
import os
import tempfile


def atomic_write_json(data, target_path):
    directory = os.path.dirname(target_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", dir=directory, delete=False, encoding="utf-8") as tmp_file:
        json.dump(data, tmp_file, indent=2)
        temp_path = tmp_file.name

    os.replace(temp_path, target_path)
