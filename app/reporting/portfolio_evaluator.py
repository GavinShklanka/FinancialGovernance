"""
Antigravity — Portfolio Evaluator.

Generates deterministic AssetDecision objects from pipeline outputs.
No LLM calls. Recommendations are computed from signal scores,
regime context, and engine allocation weights.

Then generates simple and analyst summaries from those deterministic fields.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from app.models import SignalSnapshot, MacroRegime, Portfolio, GovernanceResult
from app.reporting.report_schema import (
    AssetDecision,
    EngineEvaluation,
    PortfolioEvaluationReport,
)

# ── Asset thesis database ────────────────────────────────────────────────────

_ASSET_INTEL: dict[str, dict] = {
    "SMH": {
        "thesis": "Semiconductor ETF captures the entire AI compute supply chain.",
        "advantage": "Diversified exposure across NVDA, AMD, TSM, ASML.",
        "risk": "Concentration in cyclical capex-dependent segment.",
        "invalidation": "Hyperscaler capex guidance cuts >15% or VIX >35.",
        "timeframe": "3-6 months",
    },
    "SOXX": {
        "thesis": "Broader semiconductor index with balanced fabless/foundry exposure.",
        "advantage": "Lower single-stock concentration than SMH.",
        "risk": "Sensitive to inventory correction cycles.",
        "invalidation": "Semi equipment orders turn negative YoY.",
        "timeframe": "3-6 months",
    },
    "NVDA": {
        "thesis": "Dominant AI training hardware provider with monopoly pricing power.",
        "advantage": "CUDA ecosystem lock-in, data center revenue acceleration.",
        "risk": "High valuation, customer custom silicon competition.",
        "invalidation": "H100/H200 demand decelerates or CUDA alternatives gain traction.",
        "timeframe": "6-12 months",
    },
    "COPX": {
        "thesis": "Copper miners benefit from AI data center power infrastructure buildout.",
        "advantage": "Structural demand from electrification and data centers.",
        "risk": "China demand slowdown, inventory rebuilds.",
        "invalidation": "Copper inventories >250kt or China PMI <48.",
        "timeframe": "3-6 months",
    },
    "URNM": {
        "thesis": "Uranium miners positioned for nuclear renaissance driven by AI power demand.",
        "advantage": "Supply deficit persists, utility contracts repricing higher.",
        "risk": "Regulatory setbacks, Kazatomprom supply expansion.",
        "invalidation": "Uranium spot <$70/lb or major reactor cancellations.",
        "timeframe": "6-12 months",
    },
    "CIBR": {
        "thesis": "Cybersecurity ETF benefits from elevated threat environment.",
        "advantage": "Non-discretionary security spend regardless of macro regime.",
        "risk": "Compression of security budgets in deep recession.",
        "invalidation": "Cyber incident rates normalize below 30/week baseline.",
        "timeframe": "1-3 months",
    },
    "GLD": {
        "thesis": "Gold provides monetary debasement hedge and portfolio stability.",
        "advantage": "Zero counterparty risk, central bank demand supportive.",
        "risk": "Rising real yields reduce gold's relative attractiveness.",
        "invalidation": "Real 10Y yield >2.5% or DXY >115.",
        "timeframe": "6-12 months",
    },
    "ITA": {
        "thesis": "Defense ETF captures geopolitical spending cycle.",
        "advantage": "Multi-year procurement contracts provide revenue visibility.",
        "risk": "Budget sequestration or political reallocation.",
        "invalidation": "Defense appropriations cut >5%.",
        "timeframe": "6-12 months",
    },
}


def _decide_action(
    allocation_pct: float,
    signal_score: float,
    stance: str,
) -> tuple[str, str]:
    """Return (action, conviction) based on deterministic rules."""
    if stance == "bearish":
        if allocation_pct >= 0.30:
            return "TRIM", "MEDIUM"
        return "HOLD", "LOW"

    if stance == "neutral":
        if signal_score > 2.0:
            return "SCALE_IN", "MEDIUM"
        return "HOLD", "MEDIUM"

    # bullish
    if allocation_pct >= 0.35 and signal_score > 3.0:
        return "BUY_NOW", "HIGH"
    if allocation_pct >= 0.25:
        return "SCALE_IN", "MEDIUM"
    return "HOLD", "LOW"


def _generate_simple_summary(d: AssetDecision) -> str:
    """Plain-language summary from deterministic fields."""
    action_map = {
        "BUY_NOW": f"Buy {d.ticker} now — strong conviction based on {d.engine} engine positioning.",
        "SCALE_IN": f"Start scaling into {d.ticker} over the next {d.timeframe}.",
        "HOLD": f"Hold existing {d.ticker} position. No changes recommended.",
        "TRIM": f"Consider trimming {d.ticker} — current regime is not supportive.",
        "EXIT": f"Exit {d.ticker} — invalidation conditions may be approaching.",
    }
    return action_map.get(d.action, f"{d.action} {d.ticker}.")


def _generate_analyst_summary(d: AssetDecision) -> str:
    """Analyst-grade summary from deterministic fields."""
    return (
        f"{d.ticker} ({d.action}, {d.conviction} conviction): "
        f"{d.thesis} "
        f"Target weight {d.target_weight_pct:.0%} via {d.engine} engine. "
        f"Primary risk: {d.primary_risk}. "
        f"Invalidation: {d.invalidation_trigger}."
    )


# ── Main evaluator ───────────────────────────────────────────────────────────

def evaluate_portfolio(
    signal_snapshot: SignalSnapshot,
    macro_regime: MacroRegime,
    portfolio: Portfolio,
    governance: GovernanceResult,
) -> PortfolioEvaluationReport:
    """Build a complete PortfolioEvaluationReport from pipeline outputs."""

    regime_key = macro_regime.regimes[0] if macro_regime.regimes else "no_dominant_regime"
    regime_display = regime_key.replace("_", " ").title()
    regime_rationale_str = macro_regime.regime_rationale.get(regime_key, "")

    all_decisions: list[AssetDecision] = []
    engine_evals: list[EngineEvaluation] = []

    for engine in portfolio.engines:
        engine_decisions: list[AssetDecision] = []

        for holding in engine.holdings:
            # Extract ticker — first word, stripped of parens
            raw_ticker = holding.split("(")[0].strip().split(" ")[0].upper()
            # Only generate decisions for recognized tickers
            if raw_ticker not in _ASSET_INTEL:
                continue
            ticker = raw_ticker
            intel = _ASSET_INTEL[ticker]

            action, conviction = _decide_action(
                engine.allocation_pct,
                signal_snapshot.total_score,
                portfolio.stance,
            )

            # Find supporting signals
            supporting = []
            for sig in signal_snapshot.signals:
                if sig.score > 0:
                    supporting.append(f"{sig.name} ({sig.score:+.1f})")

            decision = AssetDecision(
                ticker=ticker,
                action=action,
                conviction=conviction,
                target_weight_pct=engine.allocation_pct / max(len(engine.holdings), 1),
                engine=engine.name,
                supporting_signals=supporting[:3],
                regime_alignment=regime_display,
                thesis=intel.get("thesis", f"Positioned within {engine.name}."),
                advantage=intel.get("advantage", ""),
                primary_risk=intel.get("risk", "General market risk."),
                invalidation_trigger=intel.get("invalidation", "Signal reversal."),
                timeframe=intel.get("timeframe", "1-3 months"),
                position_size_rationale=f"{engine.allocation_pct:.0%} engine allocation across {len(engine.holdings)} holdings.",
                entry_strategy="Scale in" if action in ("SCALE_IN", "BUY_NOW") else "Hold current",
                exit_conditions=intel.get("invalidation", "Regime change or governance failure."),
            )
            decision.simple_summary = _generate_simple_summary(decision)
            decision.analyst_summary = _generate_analyst_summary(decision)

            engine_decisions.append(decision)
            all_decisions.append(decision)

        stance_label = "OVERWEIGHT" if engine.allocation_pct >= 0.35 else ("UNDERWEIGHT" if engine.allocation_pct <= 0.15 else "NEUTRAL")

        engine_evals.append(EngineEvaluation(
            engine_name=engine.name,
            allocation_pct=engine.allocation_pct,
            stance=stance_label,
            top_holdings=engine_decisions,
            rationale=engine.rationale,
            risk_summary=f"Engine risk proportional to {engine.allocation_pct:.0%} portfolio exposure.",
        ))

    # Build report-level summaries
    buy_count = sum(1 for d in all_decisions if d.action == "BUY_NOW")
    scale_count = sum(1 for d in all_decisions if d.action == "SCALE_IN")
    hold_count = sum(1 for d in all_decisions if d.action == "HOLD")
    trim_count = sum(1 for d in all_decisions if d.action in ("TRIM", "EXIT"))

    simple = (
        f"Portfolio stance: {portfolio.stance.upper()}. "
        f"{buy_count} buy, {scale_count} scale-in, {hold_count} hold, {trim_count} trim. "
        f"Cash reserve: {portfolio.cash_pct:.0%}."
    )

    analyst = (
        f"Active regime: {regime_display}. Total signal score: {signal_snapshot.total_score:+.2f}. "
        f"The three-engine model recommends {portfolio.stance} positioning with "
        f"{portfolio.cash_pct:.0%} cash. "
        f"{'Governance passed.' if governance.passed else f'Governance FAILED with {len(governance.violations)} violation(s).'}"
    )

    execution = (
        f"Execution priority: "
        + (f"{buy_count} immediate buys. " if buy_count else "")
        + (f"{scale_count} scale-in positions. " if scale_count else "")
        + (f"{trim_count} trims. " if trim_count else "")
        + f"Review in Wealthsimple TFSA."
    )

    report = PortfolioEvaluationReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        regime=regime_display,
        regime_rationale=regime_rationale_str,
        stance=portfolio.stance,
        total_signal_score=signal_snapshot.total_score,
        cash_pct=portfolio.cash_pct,
        engines=engine_evals,
        decisions=all_decisions,
        governance_passed=governance.passed,
        governance_notes=[n for n in governance.notes],
        simple_summary=simple,
        analyst_summary=analyst,
        execution_summary=execution,
        report_id=str(uuid.uuid4())[:8],
    )

    return report
