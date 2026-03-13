"""
Antigravity — Snapshot Validator
Validates JSON structures before atomic writes to prevent corruption.
"""

def validate_json_structure(data: dict, required_fields: list) -> bool:
    """Verifies that all required fields are present in the snapshot data."""
    for field in required_fields:
        if field not in data:
            raise ValueError(f"[Snapshot Error] Missing required field: {field}")
    return True
