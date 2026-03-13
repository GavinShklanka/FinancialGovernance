"""
Antigravity — Signal scoring engine (Stage 2).

Converts raw MarketSnapshot data into a scored SignalSnapshot.
Each signal returns: name, value, score (+1/-1/0), weight, explanation.

Signals scored:
  Core: VIX, DXY, 10Y Yield, Gold, BTC
  Extended: Copper inventories, Uranium spot, Semi equipment orders,
            Hyperscaler capex, Cyber incidents, China PMI, Electricity demand

Output saved to: data/processed/signal_snapshot.json
"""

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone

from app.models import MarketSnapshot, Signal, SignalSnapshot
from system_integrity.atomic_writer import atomic_write_json
from system_integrity.snapshot_validator import validate_json_structure
from system_integrity.recovery_manager import backup_snapshot


PROCESSED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "processed"
)
SIGNAL_SNAPSHOT_PATH = os.path.join(PROCESSED_DIR, "signal_snapshot.json")


# ── Core signal scorers ──────────────────────────────────────────────────────

def _score_vix(vix: float) -> Signal:
    """VIX < 15 → calm markets (bullish); > 25 → fear (bearish)."""
    if vix < 15:
        score, expl = 1.0, f"VIX {vix} — low volatility, risk-on environment."
    elif vix > 25:
        score, expl = -1.0, f"VIX {vix} — elevated fear, risk-off signal."
    else:
        score, expl = 0.0, f"VIX {vix} — neutral range, no directional edge."
    return Signal(name="VIX Level", value=vix, score=score, weight=1.5, explanation=expl)


def _score_dxy(dxy: float) -> Signal:
    """Strong dollar (> 105) pressures commodities and risk assets."""
    if dxy > 105:
        score, expl = -1.0, f"DXY {dxy} — strong dollar headwind for commodities and EM."
    elif dxy < 100:
        score, expl = 1.0, f"DXY {dxy} — weak dollar tailwind for risk assets and commodities."
    else:
        score, expl = 0.0, f"DXY {dxy} — neutral dollar range."
    return Signal(name="DXY Strength", value=dxy, score=score, weight=1.0, explanation=expl)


def _score_yield(tnx_yield: float) -> Signal:
    """Rising yields (> 4.5%) compress equity multiples."""
    if tnx_yield > 4.5:
        score, expl = -1.0, f"10Y yield {tnx_yield}% — restrictive territory, multiple compression risk."
    elif tnx_yield < 3.5:
        score, expl = 1.0, f"10Y yield {tnx_yield}% — accommodative, supportive for growth equities."
    else:
        score, expl = 0.0, f"10Y yield {tnx_yield}% — neutral range."
    return Signal(name="10Y Yield", value=tnx_yield, score=score, weight=1.2, explanation=expl)


def _score_gold(gold_price: float) -> Signal:
    """Gold above $2,100 signals risk-off / inflation hedging demand."""
    if gold_price > 2100:
        score, expl = -0.5, f"Gold ${gold_price:,.0f} — elevated, signalling defensive demand."
    else:
        score, expl = 0.5, f"Gold ${gold_price:,.0f} — below risk-off threshold, risk-on leaning."
    return Signal(name="Gold Momentum", value=gold_price, score=score, weight=0.8, explanation=expl)


def _score_btc(btc_price: float) -> Signal:
    """BTC above $60k → risk-on sentiment indicator."""
    if btc_price > 60000:
        score, expl = 1.0, f"BTC ${btc_price:,.0f} — above $60k, strong risk-on signal."
    elif btc_price < 30000:
        score, expl = -1.0, f"BTC ${btc_price:,.0f} — below $30k, risk-off sentiment."
    else:
        score, expl = 0.0, f"BTC ${btc_price:,.0f} — mid-range, no strong directional signal."
    return Signal(name="BTC Momentum", value=btc_price, score=score, weight=0.7, explanation=expl)


# ── Extended signal scorers ──────────────────────────────────────────────────

def _score_copper(copper_inventories: float) -> Signal:
    """Falling LME copper inventories (< 200kt) → supply tightness, bullish copper/COPX."""
    if copper_inventories < 150:
        score, expl = 1.0, f"Copper inventories {copper_inventories}kt — critically low, strong bullish signal for COPX."
    elif copper_inventories < 200:
        score, expl = 0.5, f"Copper inventories {copper_inventories}kt — below 200kt threshold, bullish for copper miners."
    elif copper_inventories > 350:
        score, expl = -1.0, f"Copper inventories {copper_inventories}kt — elevated, bearish oversupply signal."
    else:
        score, expl = 0.0, f"Copper inventories {copper_inventories}kt — neutral range."
    return Signal(name="Copper Inventories", value=copper_inventories, score=score, weight=1.2, explanation=expl)


def _score_uranium(uranium_spot: float) -> Signal:
    """Uranium spot > $90/lb → supply deficit thesis intact, bullish URNM."""
    if uranium_spot > 90:
        score, expl = 1.0, f"Uranium spot ${uranium_spot}/lb — above $90, supply deficit intact, bullish URNM."
    elif uranium_spot > 70:
        score, expl = 0.5, f"Uranium spot ${uranium_spot}/lb — elevated but below peak, moderately bullish."
    elif uranium_spot < 50:
        score, expl = -1.0, f"Uranium spot ${uranium_spot}/lb — depressed, thesis weakening."
    else:
        score, expl = 0.0, f"Uranium spot ${uranium_spot}/lb — neutral range."
    return Signal(name="Uranium Spot", value=uranium_spot, score=score, weight=1.1, explanation=expl)


def _score_semis(semi_equipment_orders: float) -> Signal:
    """SEMI billings > 10% YoY → semiconductor capex expansion, bullish SMH."""
    if semi_equipment_orders > 15:
        score, expl = 1.0, f"SEMI billings +{semi_equipment_orders}% YoY — strong capex cycle, bullish SMH."
    elif semi_equipment_orders > 5:
        score, expl = 0.5, f"SEMI billings +{semi_equipment_orders}% YoY — expanding, moderately bullish."
    elif semi_equipment_orders < 0:
        score, expl = -1.0, f"SEMI billings {semi_equipment_orders}% YoY — contracting, bearish for semis."
    else:
        score, expl = 0.0, f"SEMI billings +{semi_equipment_orders}% YoY — flat, neutral."
    return Signal(name="Semi Equipment Orders", value=semi_equipment_orders, score=score, weight=1.3, explanation=expl)


def _score_hyperscaler_capex(hyperscaler_capex_signal: float) -> Signal:
    """Hyperscaler capex signal (0–10) > 7 → AI infrastructure buildout, bullish semi/power."""
    if hyperscaler_capex_signal >= 7.0:
        score, expl = 1.0, f"Hyperscaler capex signal {hyperscaler_capex_signal}/10 — strong AI infrastructure spend, bullish semis and power."
    elif hyperscaler_capex_signal >= 5.0:
        score, expl = 0.5, f"Hyperscaler capex signal {hyperscaler_capex_signal}/10 — moderate spend, neutral to bullish."
    elif hyperscaler_capex_signal < 3.0:
        score, expl = -1.0, f"Hyperscaler capex signal {hyperscaler_capex_signal}/10 — weak, AI spend cooling."
    else:
        score, expl = 0.0, f"Hyperscaler capex signal {hyperscaler_capex_signal}/10 — neutral."
    return Signal(name="Hyperscaler Capex", value=hyperscaler_capex_signal, score=score, weight=1.4, explanation=expl)


def _score_cyber(cyber_incidents: float) -> Signal:
    """Rising cyber incidents > 50/week → sector tailwind for cybersecurity stocks."""
    if cyber_incidents > 60:
        score, expl = 1.0, f"{cyber_incidents:.0f} cyber incidents/week — elevated threat environment, strong tailwind for cybersecurity sector."
    elif cyber_incidents > 40:
        score, expl = 0.5, f"{cyber_incidents:.0f} cyber incidents/week — moderate threat level, mild bullish for cybersecurity."
    else:
        score, expl = 0.0, f"{cyber_incidents:.0f} cyber incidents/week — below elevated threshold, neutral."
    return Signal(name="Cyber Incidents", value=cyber_incidents, score=score, weight=0.9, explanation=expl)


def _score_china_pmi(china_pmi: float) -> Signal:
    """China PMI > 50 → expansion, positive for global commodity demand."""
    if china_pmi > 51:
        score, expl = 1.0, f"China PMI {china_pmi} — strong expansion, commodity demand supportive."
    elif china_pmi > 50:
        score, expl = 0.5, f"China PMI {china_pmi} — modest expansion above 50, mildly bullish for commodities."
    elif china_pmi < 49:
        score, expl = -1.0, f"China PMI {china_pmi} — contraction, bearish for commodity demand."
    else:
        score, expl = 0.0, f"China PMI {china_pmi} — borderline neutral."
    return Signal(name="China PMI", value=china_pmi, score=score, weight=1.0, explanation=expl)


def _score_electricity(electricity_demand_signal: float) -> Signal:
    """US electricity demand growth > 3% YoY → AI/data center buildout signal."""
    if electricity_demand_signal > 3.0:
        score, expl = 1.0, f"Electricity demand +{electricity_demand_signal}% YoY — AI/data center buildout driving demand, bullish for power and infrastructure."
    elif electricity_demand_signal > 1.0:
        score, expl = 0.5, f"Electricity demand +{electricity_demand_signal}% YoY — growing, moderately bullish."
    elif electricity_demand_signal < 0:
        score, expl = -1.0, f"Electricity demand {electricity_demand_signal}% YoY — contracting, bearish signal."
    else:
        score, expl = 0.0, f"Electricity demand +{electricity_demand_signal}% YoY — flat, neutral."
    return Signal(name="Electricity Demand", value=electricity_demand_signal, score=score, weight=1.1, explanation=expl)


# ── Public API ───────────────────────────────────────────────────────────────

def score_signals(snapshot: MarketSnapshot) -> SignalSnapshot:
    """Score all signals and return enriched snapshot. Also saves JSON."""

    signals = [
        # Core
        _score_vix(snapshot.vix),
        _score_dxy(snapshot.dxy),
        _score_yield(snapshot.tnx_yield),
        _score_gold(snapshot.gold_price),
        _score_btc(snapshot.btc_price),
        # Extended
        _score_copper(snapshot.copper_inventories),
        _score_uranium(snapshot.uranium_spot),
        _score_semis(snapshot.semi_equipment_orders),
        _score_hyperscaler_capex(snapshot.hyperscaler_capex_signal),
        _score_cyber(snapshot.cyber_incidents),
        _score_china_pmi(snapshot.china_pmi),
        _score_electricity(snapshot.electricity_demand_signal),
    ]

    total_score = round(sum(s.score * s.weight for s in signals), 2)

    signal_snapshot = SignalSnapshot(
        spy_price=snapshot.spy_price,
        vix=snapshot.vix,
        dxy=snapshot.dxy,
        tnx_yield=snapshot.tnx_yield,
        gold_price=snapshot.gold_price,
        btc_price=snapshot.btc_price,
        copper_inventories=snapshot.copper_inventories,
        uranium_spot=snapshot.uranium_spot,
        semi_equipment_orders=snapshot.semi_equipment_orders,
        hyperscaler_capex_signal=snapshot.hyperscaler_capex_signal,
        cyber_incidents=snapshot.cyber_incidents,
        china_pmi=snapshot.china_pmi,
        electricity_demand_signal=snapshot.electricity_demand_signal,
        timestamp=snapshot.timestamp,
        total_score=total_score,
        signals=signals,
    )

    _save_signal_snapshot(signal_snapshot)
    return signal_snapshot


def _save_signal_snapshot(ss: SignalSnapshot) -> None:
    """Persist the signal snapshot to data/processed/signal_snapshot.json."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    payload = {
        "timestamp": ss.timestamp,
        "total_score": ss.total_score,
        "market_data": {
            "spy_price": ss.spy_price,
            "vix": ss.vix,
            "dxy": ss.dxy,
            "tnx_yield": ss.tnx_yield,
            "gold_price": ss.gold_price,
            "btc_price": ss.btc_price,
            "copper_inventories": ss.copper_inventories,
            "uranium_spot": ss.uranium_spot,
            "semi_equipment_orders": ss.semi_equipment_orders,
            "hyperscaler_capex_signal": ss.hyperscaler_capex_signal,
            "cyber_incidents": ss.cyber_incidents,
            "china_pmi": ss.china_pmi,
            "electricity_demand_signal": ss.electricity_demand_signal,
        },
        "signals": [
            {
                "name": s.name,
                "value": s.value,
                "score": s.score,
                "weight": s.weight,
                "explanation": s.explanation,
            }
            for s in ss.signals
        ],
    }

    backup_snapshot(SIGNAL_SNAPSHOT_PATH)
    validate_json_structure(payload, ["timestamp", "total_score", "signals"])
    atomic_write_json(payload, SIGNAL_SNAPSHOT_PATH)

    print(f"  [Stage 2] Signal snapshot saved → {SIGNAL_SNAPSHOT_PATH}")
