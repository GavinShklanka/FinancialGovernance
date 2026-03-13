"""
Antigravity — State Versioning Manager
Captures full system state (pipelines outputs) grouped by weekly run intoversioned folders.
"""

import os
import shutil
import json
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(ROOT_DIR, "state", "versions")
METADATA_DIR = os.path.join(ROOT_DIR, "state", "metadata")
REGISTRY_PATH = os.path.join(METADATA_DIR, "state_registry.json")

def create_state_snapshot(signal_score: float, regimes: list, portfolio_stance: str):
    date = datetime.now(timezone.utc).strftime("%Y_%m_%d")
    version_path = os.path.join(STATE_DIR, date)

    os.makedirs(version_path, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)

    files = [
        "data/raw/market_snapshot.json",
        "data/processed/signal_snapshot.json",
        "macro_regime/regime_snapshot.json",
        "portfolio_model.json",
        "decision_graph.json"
    ]

    for rel_file in files:
        full_path = os.path.join(ROOT_DIR, rel_file)
        if os.path.exists(full_path):
            shutil.copy(full_path, version_path)

    # Update metadata registry
    _update_registry(date, signal_score, regimes, portfolio_stance)
    
    print(f"  [State Versioning] Saved full state to: state/versions/{date}/")

def _update_registry(date: str, signal_score: float, regimes: list, portfolio_stance: str):
    registry = {"versions": []}
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            pass
            
    # Check if entry already exists
    for entry in registry["versions"]:
        if entry["date"] == date:
            entry["signal_score"] = signal_score
            entry["regimes"] = regimes
            entry["portfolio_stance"] = portfolio_stance
            break
    else:
        registry["versions"].append({
            "date": date,
            "signal_score": signal_score,
            "regimes": regimes,
            "portfolio_stance": portfolio_stance
        })
        
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
