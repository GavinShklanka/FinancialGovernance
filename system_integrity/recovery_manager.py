"""
Antigravity — Recovery Manager
Restores the last good snapshot from a backup if corruption is detected.
"""

import shutil
import os


def backup_snapshot(path: str) -> None:
    """Create a backup of an existing snapshot."""
    if os.path.exists(path):
        backup_path = path + ".backup"
        shutil.copy(path, backup_path)
        print(f"    [Snapshot] Backup created: {backup_path}")


def restore_backup(snapshot_path: str) -> bool:
    """Restore from a backup if available."""
    backup_path = snapshot_path + ".backup"
    if os.path.exists(backup_path):
        shutil.copy(backup_path, snapshot_path)
        print(f"    [Recovery] Restored backup: {snapshot_path}")
        return True
    return False
