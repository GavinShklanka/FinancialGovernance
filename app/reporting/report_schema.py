"""
Antigravity — Portfolio Evaluation Report Schema.

Canonical report object generated on each pipeline run.
All fields are deterministic — no LLM output is stored here.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json


# ── Per-Asset Evaluations ────────────────────────────────────────────────────

@dataclass
class AssetDecision:
    """Deterministic recommendation for a single asset or holding."""
    ticker: str
    action: str                        # BUY_NOW | SCALE_IN | HOLD | TRIM | EXIT
    conviction: str                    # HIGH | MEDIUM | LOW
    target_weight_pct: float           # 0.0 – 1.0
    current_weight_pct: float = 0.0    # estimated current weight (placeholder)

    # Evidence layer
    supporting_signals: List[str] = field(default_factory=list)
    regime_alignment: str = ""         # e.g. "AI Infrastructure Boom"
    thesis: str = ""
    advantage: str = ""

    # Sizing
    position_size_rationale: str = ""
    engine: str = ""                   # Growth | Infrastructure | Defense

    # Risk
    primary_risk: str = ""
    invalidation_trigger: str = ""
    max_drawdown_tolerance: str = ""

    # Execution
    entry_strategy: str = ""           # e.g. "Scale in over 2 weeks"
    exit_conditions: str = ""
    timeframe: str = ""                # "1-3 months" | "3-6 months" | "6-12 months"

    # Summaries (generated from deterministic fields)
    simple_summary: str = ""
    analyst_summary: str = ""


# ── Engine-Level Evaluation ──────────────────────────────────────────────────

@dataclass
class EngineEvaluation:
    """Evaluation of an entire strategy engine."""
    engine_name: str
    allocation_pct: float
    stance: str                         # OVERWEIGHT | NEUTRAL | UNDERWEIGHT
    top_holdings: List[AssetDecision] = field(default_factory=list)
    rationale: str = ""
    risk_summary: str = ""


# ── Top-Level Portfolio Evaluation Report ────────────────────────────────────

@dataclass
class PortfolioEvaluationReport:
    """Canonical portfolio evaluation — usable in UI and export."""
    timestamp: str = ""
    regime: str = ""
    regime_rationale: str = ""
    stance: str = ""                    # bullish | neutral | bearish
    total_signal_score: float = 0.0
    cash_pct: float = 0.0

    # Per-engine evaluations
    engines: List[EngineEvaluation] = field(default_factory=list)

    # Flattened asset decisions for quick card rendering
    decisions: List[AssetDecision] = field(default_factory=list)

    # Governance
    governance_passed: bool = True
    governance_notes: List[str] = field(default_factory=list)

    # Report-level summaries
    simple_summary: str = ""
    analyst_summary: str = ""
    execution_summary: str = ""

    # Metadata
    pipeline_version: str = "1.0"
    report_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict) -> PortfolioEvaluationReport:
        engines = [
            EngineEvaluation(
                engine_name=e["engine_name"],
                allocation_pct=e["allocation_pct"],
                stance=e.get("stance", "NEUTRAL"),
                top_holdings=[AssetDecision(**h) for h in e.get("top_holdings", [])],
                rationale=e.get("rationale", ""),
                risk_summary=e.get("risk_summary", ""),
            )
            for e in data.get("engines", [])
        ]
        decisions = [AssetDecision(**d) for d in data.get("decisions", [])]

        return cls(
            timestamp=data.get("timestamp", ""),
            regime=data.get("regime", ""),
            regime_rationale=data.get("regime_rationale", ""),
            stance=data.get("stance", ""),
            total_signal_score=data.get("total_signal_score", 0.0),
            cash_pct=data.get("cash_pct", 0.0),
            engines=engines,
            decisions=decisions,
            governance_passed=data.get("governance_passed", True),
            governance_notes=data.get("governance_notes", []),
            simple_summary=data.get("simple_summary", ""),
            analyst_summary=data.get("analyst_summary", ""),
            execution_summary=data.get("execution_summary", ""),
            pipeline_version=data.get("pipeline_version", "1.0"),
            report_id=data.get("report_id", ""),
        )
