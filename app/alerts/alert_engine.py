"""
Antigravity — Alert Engine (Upgrade 3).

Notifies the operator when macro signals cross critical thresholds.
Alerts indicate regime transitions or risk spikes.

Output is saved to data/processed/alerts.json
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List

from app.models import MarketSnapshot

PROCESSED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed"
)
ALERTS_PATH = os.path.join(PROCESSED_DIR, "alerts.json")


@dataclass
class Alert:
    level: str  # "WARNING" or "CRITICAL"
    message: str


def generate_alerts(snapshot: MarketSnapshot) -> List[Alert]:
    """Evaluate market snapshot against critical alert thresholds."""
    alerts = []

    if snapshot.vix > 30:
        alerts.append(Alert("CRITICAL", "Volatility crisis detected (VIX > 30)"))
        
    if snapshot.copper_inventories < 120:
        alerts.append(Alert("WARNING", "Copper supply shock (Inventories critically low)"))
        
    if snapshot.semi_equipment_orders > 15:
        alerts.append(Alert("WARNING", "AI compute demand surge (Semi orders > 15% YoY)"))
        
    if snapshot.dxy > 115:
        alerts.append(Alert("CRITICAL", "Global liquidity contraction (DXY > 115)"))

    _save_alerts(alerts)
    return alerts


def _save_alerts(alerts: List[Alert]) -> None:
    """Save generated alerts to processed directory."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    payload = {
        "alerts": [asdict(a) for a in alerts]
    }
    with open(ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    
    print(f"  [Alert Engine] Saved {len(alerts)} system alerts → {ALERTS_PATH}")
