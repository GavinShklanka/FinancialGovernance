"""
Antigravity — Core data models.

Defines the data structures that flow through the full 8-stage pipeline:
  MarketSnapshot → SignalSnapshot → MacroRegime → Portfolio → GovernanceResult
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ── Stage 1 ─────────────────────────────────────────────────────────────────

@dataclass
class MarketSnapshot:
    """Raw market data collected in a single fetch."""
    # Core macro indicators
    spy_price: float
    vix: float
    dxy: float
    tnx_yield: float
    gold_price: float
    btc_price: float
    timestamp: str

    # Extended macro signals (Stage 1 expansion)
    copper_inventories: float = 0.0        # LME copper stocks (kt) — falling = bullish
    uranium_spot: float = 0.0              # U3O8 spot price USD/lb
    semi_equipment_orders: float = 0.0    # SEMI billings index (% YoY)
    hyperscaler_capex_signal: float = 0.0 # Composite hyperscaler capex momentum (0–10)
    cyber_incidents: float = 0.0          # Weekly incident count (public sources)
    china_pmi: float = 0.0                # China official manufacturing PMI
    electricity_demand_signal: float = 0.0 # US electricity demand growth % YoY
    equities: Dict[str, Dict[str, float | str]] = field(default_factory=dict)
    macro: Dict[str, Dict[str, float | str]] = field(default_factory=dict)
    crypto: Dict[str, Dict[str, float | str]] = field(default_factory=dict)


# ── Stage 2 ─────────────────────────────────────────────────────────────────

@dataclass
class Signal:
    """An individual scored signal derived from market data."""
    name: str
    value: float
    score: float           # +1 bullish, 0 neutral, -1 bearish
    weight: float = 1.0
    explanation: str = ""  # Human-readable rationale


@dataclass
class SignalSnapshot:
    """Market snapshot enriched with scored signals."""
    spy_price: float
    vix: float
    dxy: float
    tnx_yield: float
    gold_price: float
    btc_price: float
    copper_inventories: float
    uranium_spot: float
    semi_equipment_orders: float
    hyperscaler_capex_signal: float
    cyber_incidents: float
    china_pmi: float
    electricity_demand_signal: float
    timestamp: str
    total_score: float = 0.0
    signals: List[Signal] = field(default_factory=list)


# ── Stage 3 ─────────────────────────────────────────────────────────────────

@dataclass
class MacroRegime:
    """Detected macro regimes for the current cycle."""
    timestamp: str
    regimes: List[str] = field(default_factory=list)
    regime_rationale: Dict[str, str] = field(default_factory=dict)


# ── Stage 4 ─────────────────────────────────────────────────────────────────

@dataclass
class Engine:
    """A single engine within the three-engine portfolio model."""
    name: str                                        # Growth / Infrastructure / Defense
    allocation_pct: float                            # 0.0 – 1.0
    holdings: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class Portfolio:
    """Portfolio recommendation derived from signal + regime analysis."""
    stance: str                                      # bullish / neutral / bearish
    engines: List[Engine] = field(default_factory=list)
    cash_pct: float = 0.10
    rationale: str = ""

    # Legacy allocations dict retained for backward compat
    allocations: Dict[str, float] = field(default_factory=dict)


# ── Stage 5 ─────────────────────────────────────────────────────────────────

@dataclass
class PolicyViolation:
    """A single governance policy violation."""
    rule: str
    detail: str
    severity: str = "WARNING"  # WARNING or CRITICAL


@dataclass
class GovernanceResult:
    """Output from the governance & policy engine."""
    passed: bool
    violations: List[PolicyViolation] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
