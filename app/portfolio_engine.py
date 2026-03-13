"""
Antigravity — Portfolio Engine (Stage 4): Three-Engine Model.

Maps signal scores + macro regimes into a structured three-engine portfolio.

Engines:
  Growth Engine       — AI software, semiconductors, high-beta tech
  Infrastructure Engine — Commodities, energy infrastructure, power
  Defense Engine      — Cybersecurity, defense tech, pipelines, TBills

Allocation weights shift based on the active macro regime.
Output saved to: portfolio_model.json
"""

import json
import os
from datetime import datetime, timezone

from app.models import SignalSnapshot, MacroRegime, Portfolio, Engine
from system_integrity.atomic_writer import atomic_write_json
from system_integrity.snapshot_validator import validate_json_structure
from system_integrity.recovery_manager import backup_snapshot


PORTFOLIO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "portfolio_model.json"
)


# ── Engine definitions by regime ─────────────────────────────────────────────

_ENGINE_PRESETS: dict[str, dict] = {

    "ai_infrastructure_boom": {
        "stance": "bullish",
        "growth": {
            "allocation_pct": 0.40,
            "holdings": ["SMH", "SOXX", "AI software (HACK, BOTZ)", "NVDA"],
            "rationale": "AI capex cycle driving semiconductor and software demand.",
        },
        "infrastructure": {
            "allocation_pct": 0.35,
            "holdings": ["COPX", "URNM", "NEE", "Power infrastructure ETFs"],
            "rationale": "AI data centers driving copper and electricity demand.",
        },
        "defense": {
            "allocation_pct": 0.15,
            "holdings": ["CIBR", "Cybersecurity names", "ITA (defense tech)"],
            "rationale": "Cyber incidents elevated — maintain cybersecurity floor position.",
        },
        "cash_pct": 0.10,
    },

    "commodity_supercycle": {
        "stance": "bullish",
        "growth": {
            "allocation_pct": 0.20,
            "holdings": ["SMH", "Commodity-adjacent tech"],
            "rationale": "Growth position maintained but de-emphasized vs infrastructure.",
        },
        "infrastructure": {
            "allocation_pct": 0.50,
            "holdings": ["COPX", "URNM", "XLE", "Pipelines", "Commodity ETFs"],
            "rationale": "Commodity supercycle — maximum infrastructure weight.",
        },
        "defense": {
            "allocation_pct": 0.15,
            "holdings": ["CIBR", "Gold miners", "GLD"],
            "rationale": "Gold and defense hedge against commodity volatility.",
        },
        "cash_pct": 0.15,
    },

    "liquidity_contraction": {
        "stance": "neutral",
        "growth": {
            "allocation_pct": 0.20,
            "holdings": ["Quality growth names", "Low-leverage tech"],
            "rationale": "Reduce high-multiple growth exposure in rising yield environment.",
        },
        "infrastructure": {
            "allocation_pct": 0.25,
            "holdings": ["Pipelines", "Real assets", "Energy infrastructure"],
            "rationale": "Real assets provide inflation protection during contraction.",
        },
        "defense": {
            "allocation_pct": 0.35,
            "holdings": ["CIBR", "ITA", "GLD", "Short-duration bonds"],
            "rationale": "Defensive overweight — VIX elevated, DXY strong.",
        },
        "cash_pct": 0.20,
    },

    "defensive_regime": {
        "stance": "bearish",
        "growth": {
            "allocation_pct": 0.10,
            "holdings": ["Minimal growth exposure"],
            "rationale": "Aggregate signal score negative — minimize risk assets.",
        },
        "infrastructure": {
            "allocation_pct": 0.20,
            "holdings": ["Pipelines", "Utilities", "Real assets"],
            "rationale": "Defensive real assets only — avoid cyclicals.",
        },
        "defense": {
            "allocation_pct": 0.40,
            "holdings": ["GLD", "Short T-Bills", "CIBR", "ITA", "Cash equivalents"],
            "rationale": "Maximum defensive posture — capital preservation priority.",
        },
        "cash_pct": 0.30,
    },

    "no_dominant_regime": {
        "stance": "neutral",
        "growth": {
            "allocation_pct": 0.30,
            "holdings": ["SMH", "QQQ", "Diversified growth"],
            "rationale": "Balanced allocation — no dominant regime signal.",
        },
        "infrastructure": {
            "allocation_pct": 0.30,
            "holdings": ["COPX", "URNM", "Energy infrastructure"],
            "rationale": "Equal-weight infrastructure for diversification.",
        },
        "defense": {
            "allocation_pct": 0.25,
            "holdings": ["CIBR", "GLD", "ITA"],
            "rationale": "Standard defense allocation for uncertainty.",
        },
        "cash_pct": 0.15,
    },
}


# ── Public API ───────────────────────────────────────────────────────────────

def build_portfolio(
    signal_snapshot: SignalSnapshot,
    macro_regime: MacroRegime | None = None,
) -> Portfolio:
    """Build portfolio using three-engine model based on macro regime."""

    # Select regime preset — use first active regime, or default
    regime_key = "no_dominant_regime"
    if macro_regime and macro_regime.regimes:
        # Priority order: defensive > liquidity > ai_boom > commodity
        priority = [
            "defensive_regime",
            "liquidity_contraction",
            "ai_infrastructure_boom",
            "commodity_supercycle",
        ]
        for p in priority:
            if p in macro_regime.regimes:
                regime_key = p
                break
        else:
            regime_key = macro_regime.regimes[0]

    preset = _ENGINE_PRESETS.get(regime_key, _ENGINE_PRESETS["no_dominant_regime"])

    growth_engine = Engine(
        name="Growth Engine",
        allocation_pct=preset["growth"]["allocation_pct"],
        holdings=preset["growth"]["holdings"],
        rationale=preset["growth"]["rationale"],
    )
    infra_engine = Engine(
        name="Infrastructure Engine",
        allocation_pct=preset["infrastructure"]["allocation_pct"],
        holdings=preset["infrastructure"]["holdings"],
        rationale=preset["infrastructure"]["rationale"],
    )
    defense_engine = Engine(
        name="Defense Engine",
        allocation_pct=preset["defense"]["allocation_pct"],
        holdings=preset["defense"]["holdings"],
        rationale=preset["defense"]["rationale"],
    )

    portfolio = Portfolio(
        stance=preset["stance"],
        engines=[growth_engine, infra_engine, defense_engine],
        cash_pct=preset["cash_pct"],
        rationale=(
            f"Regime: {regime_key.replace('_', ' ').title()}. "
            f"Signal score: {signal_snapshot.total_score:+.2f}. "
            f"Three-engine model applied."
        ),
        # Legacy compat
        allocations={
            "growth":         growth_engine.allocation_pct,
            "infrastructure": infra_engine.allocation_pct,
            "defense":        defense_engine.allocation_pct,
            "cash":           preset["cash_pct"],
        },
    )

    _save_portfolio_model(portfolio, regime_key)
    return portfolio


def _save_portfolio_model(portfolio: Portfolio, regime_key: str) -> None:
    """Persist portfolio model to portfolio_model.json."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stance": portfolio.stance,
        "regime_applied": regime_key,
        "cash_pct": portfolio.cash_pct,
        "engines": [
            {
                "name": e.name,
                "allocation_pct": e.allocation_pct,
                "holdings": e.holdings,
                "rationale": e.rationale,
            }
            for e in portfolio.engines
        ],
        "rationale": portfolio.rationale,
    }

    backup_snapshot(PORTFOLIO_PATH)
    validate_json_structure(payload, ["timestamp", "stance", "engines"])
    atomic_write_json(payload, PORTFOLIO_PATH)

    print(f"  [Stage 4] Portfolio model saved → {PORTFOLIO_PATH}")
    print(f"            Stance: {portfolio.stance.upper()}  |  Regime: {regime_key}")
