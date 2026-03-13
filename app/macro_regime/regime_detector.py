"""
Antigravity — Macro Regime Detector (Stage 3).

Interprets scored signal data to classify the current macro environment
into one or more named regimes. Multiple regimes can be active simultaneously.

Possible regimes:
  ai_infrastructure_boom   — semi demand ↑, electricity demand ↑, hyperscaler capex ↑
  commodity_supercycle     — copper ↑, uranium ↑, China PMI ↑
  liquidity_contraction    — yields ↑, DXY ↑, VIX ↑
  defensive_regime         — net bearish signal score, multiple risk-off signals firing

Output saved to: macro_regime/regime_snapshot.json
"""

import json
import os
from datetime import datetime, timezone

from app.models import SignalSnapshot, MacroRegime
from system_integrity.atomic_writer import atomic_write_json
from system_integrity.snapshot_validator import validate_json_structure
from system_integrity.recovery_manager import backup_snapshot


REGIME_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "macro_regime"
)
REGIME_PATH = os.path.join(REGIME_DIR, "regime_snapshot.json")


# ── Regime detection rules ───────────────────────────────────────────────────

def _detect_ai_infrastructure_boom(ss: SignalSnapshot) -> tuple[bool, str]:
    """Fire when semis, electricity demand, and hyperscaler capex are all bullish."""
    semi_ok     = ss.semi_equipment_orders > 10
    elec_ok     = ss.electricity_demand_signal > 2.5
    capex_ok    = ss.hyperscaler_capex_signal >= 7.0
    active      = semi_ok and elec_ok and capex_ok
    rationale   = (
        f"Semi orders +{ss.semi_equipment_orders:.1f}% YoY, "
        f"electricity demand +{ss.electricity_demand_signal:.1f}% YoY, "
        f"hyperscaler capex signal {ss.hyperscaler_capex_signal:.1f}/10. "
        "AI infrastructure buildout confirmed."
    ) if active else ""
    return active, rationale


def _detect_commodity_supercycle(ss: SignalSnapshot) -> tuple[bool, str]:
    """Fire when copper is tight, uranium is elevated, and China PMI is expansionary."""
    copper_ok   = ss.copper_inventories < 250
    uranium_ok  = ss.uranium_spot > 75
    pmi_ok      = ss.china_pmi > 50
    active      = copper_ok and uranium_ok and pmi_ok
    rationale   = (
        f"Copper inventories {ss.copper_inventories:.0f}kt (tight), "
        f"uranium spot ${ss.uranium_spot:.0f}/lb, "
        f"China PMI {ss.china_pmi:.1f} (expansion). "
        "Commodity supercycle conditions present."
    ) if active else ""
    return active, rationale


def _detect_liquidity_contraction(ss: SignalSnapshot) -> tuple[bool, str]:
    """Fire when yields are high, dollar is strong, and VIX is elevated."""
    yield_ok    = ss.tnx_yield > 4.3
    dxy_ok      = ss.dxy > 103
    vix_ok      = ss.vix > 20
    # Need at least 2 of 3 to confirm regime
    count       = sum([yield_ok, dxy_ok, vix_ok])
    active      = count >= 2
    rationale   = (
        f"10Y yield {ss.tnx_yield:.2f}%, DXY {ss.dxy:.1f}, VIX {ss.vix:.1f}. "
        f"{count}/3 contraction signals firing. Liquidity conditions tightening."
    ) if active else ""
    return active, rationale


def _detect_defensive_regime(ss: SignalSnapshot, total_score: float) -> tuple[bool, str]:
    """Fire when aggregate signal score is negative and gold / VIX are elevated."""
    score_bearish = total_score <= -2.0
    gold_elevated = ss.gold_price > 2100
    vix_elevated  = ss.vix > 22
    active        = score_bearish or (gold_elevated and vix_elevated)
    rationale     = (
        f"Aggregate score {total_score:.2f}, gold ${ss.gold_price:,.0f}, VIX {ss.vix:.1f}. "
        "Defensive posture warranted — reduce risk exposure."
    ) if active else ""
    return active, rationale


# ── Public API ───────────────────────────────────────────────────────────────

def detect_regime(ss: SignalSnapshot) -> MacroRegime:
    """Run all regime detectors and return active regimes."""

    timestamp = datetime.now(timezone.utc).isoformat()
    regimes: list[str] = []
    rationale: dict[str, str] = {}

    checks = [
        ("ai_infrastructure_boom",  _detect_ai_infrastructure_boom(ss)),
        ("commodity_supercycle",     _detect_commodity_supercycle(ss)),
        ("liquidity_contraction",    _detect_liquidity_contraction(ss)),
        ("defensive_regime",         _detect_defensive_regime(ss, ss.total_score)),
    ]

    for regime_key, (active, reason) in checks:
        if active:
            regimes.append(regime_key)
            rationale[regime_key] = reason

    if not regimes:
        regimes.append("no_dominant_regime")
        rationale["no_dominant_regime"] = (
            "No single macro regime threshold met. Monitor signals for emerging trend."
        )

    macro_regime = MacroRegime(
        timestamp=timestamp,
        regimes=regimes,
        regime_rationale=rationale,
    )

    _save_regime_snapshot(macro_regime)
    return macro_regime


def _save_regime_snapshot(regime: MacroRegime) -> None:
    """Persist the regime snapshot to macro_regime/regime_snapshot.json."""
    os.makedirs(REGIME_DIR, exist_ok=True)

    payload = {
        "timestamp": regime.timestamp,
        "regimes": regime.regimes,
        "regime_rationale": regime.regime_rationale,
    }

    backup_snapshot(REGIME_PATH)
    validate_json_structure(payload, ["timestamp", "regimes", "regime_rationale"])
    atomic_write_json(payload, REGIME_PATH)

    print(f"  [Stage 3] Regime snapshot saved → {REGIME_PATH}")
    print(f"            Active regimes: {', '.join(regime.regimes)}")
