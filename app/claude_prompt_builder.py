"""
Antigravity — Claude Master Prompt Builder (Stage 7).

Assembles a complete, ready-to-paste research prompt for Claude.
The prompt embeds all pipeline outputs so Claude can deliver a
structured macro investment research briefing.

Output saved to: app/outputs/claude_prompt.txt
"""

import json
import os
from datetime import datetime, timezone

from app.models import SignalSnapshot, MacroRegime, Portfolio, GovernanceResult


OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "outputs"
)
PROMPT_PATH = os.path.join(OUTPUT_DIR, "claude_prompt.txt")


# ── Formatting helpers ───────────────────────────────────────────────────────

def _format_signals(ss: SignalSnapshot) -> str:
    lines = []
    for s in ss.signals:
        direction = "▲ BULL" if s.score > 0 else ("▼ BEAR" if s.score < 0 else "● NEUTRAL")
        lines.append(f"  {direction:12s}  {s.name:28s}  Score: {s.score:+.1f}  |  {s.explanation}")
    return "\n".join(lines)


def _format_engines(portfolio: Portfolio) -> str:
    lines = []
    for e in portfolio.engines:
        lines.append(f"  {e.name} ({e.allocation_pct:.0%})")
        lines.append(f"    Holdings: {', '.join(e.holdings)}")
        lines.append(f"    Rationale: {e.rationale}")
        lines.append("")
    lines.append(f"  Cash: {portfolio.cash_pct:.0%}")
    return "\n".join(lines)


def _format_violations(gov: GovernanceResult) -> str:
    if gov.passed:
        return "  ✓ All governance policies passed."
    lines = []
    for v in gov.violations:
        lines.append(f"  [{v.severity}] {v.rule}: {v.detail}")
    return "\n".join(lines)


# ── Prompt assembly ──────────────────────────────────────────────────────────

MASTER_PROMPT_TEMPLATE = """\
================================================================================
LUMIN FINANCE RESEARCH PROMPT
Generated: {timestamp}
================================================================================

You are a macro financial strategist analyzing the AI Supercycle.

Your task is to interpret the Antigravity signal system and provide a clear investment thesis.

The system provides:
1. Macro Signals
2. Regime Detection
3. Portfolio Allocation
4. Risk Alerts
5. Regime Forecast

Your job is to:
1. Explain the current macro regime.
2. Interpret the signals driving the regime.
3. Evaluate the recommended portfolio allocation.
4. Identify macro risks.
5. Forecast potential regime transitions.
6. Recommend how a young investor should position capital during the AI Supercycle.

Important:
- Explain the reasoning clearly so the user learns how macro signals translate into investment strategy.
- Avoid short-term trading advice.
- Focus on structural trends including: AI infrastructure, semiconductors, energy demand, cybersecurity, cloud computing, defense technology, and industrial electrification.
- Use the signals provided by the Antigravity system as anchors.
- Explain: Why these signals matter. How long the regime could persist. What conditions would invalidate the thesis.

────────────────────────────────────────────────────────────────────────────────
SYSTEM DATA SNAPSHOT
────────────────────────────────────────────────────────────────────────────────

1. MACRO SIGNALS (Total Score: {total_score:+.2f})
{signal_lines}

2. REGIME DETECTION
Active Regimes: {regimes}
Rationale:
{regime_rationale}

3. PORTFOLIO ALLOCATION (Three-Engine Model)
Stance: {stance}
{engine_breakdown}
Rationale: {portfolio_rationale}

4. RISK ALERTS & GOVERNANCE
Governance: {gov_status}
{governance_detail}

────────────────────────────────────────────────────────────────────────────────
YOUR ANALYSIS (Claude)
────────────────────────────────────────────────────────────────────────────────
Please structure your response based on the 6 key jobs above, ensuring an educational narrative journey.

================================================================================
END OF LUMIN FINANCE BRIEFING
================================================================================
"""


def build_claude_prompt(
    signal_snapshot: SignalSnapshot,
    macro_regime: MacroRegime,
    portfolio: Portfolio,
    governance: GovernanceResult,
) -> str:
    """Assemble and save the Claude master research prompt."""

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    regime_rationale_str = "\n".join(
        f"  [{k.replace('_', ' ').upper()}] {v}"
        for k, v in macro_regime.regime_rationale.items()
    ) or "  No dominant regime detected."

    prompt = MASTER_PROMPT_TEMPLATE.format(
        timestamp=timestamp,
        total_score=signal_snapshot.total_score,
        spy_price=signal_snapshot.spy_price,
        vix=signal_snapshot.vix,
        dxy=signal_snapshot.dxy,
        tnx_yield=signal_snapshot.tnx_yield,
        gold_price=signal_snapshot.gold_price,
        btc_price=signal_snapshot.btc_price,
        copper_inventories=signal_snapshot.copper_inventories,
        uranium_spot=signal_snapshot.uranium_spot,
        semi_equipment_orders=signal_snapshot.semi_equipment_orders,
        hyperscaler_capex_signal=signal_snapshot.hyperscaler_capex_signal,
        cyber_incidents=signal_snapshot.cyber_incidents,
        china_pmi=signal_snapshot.china_pmi,
        electricity_demand_signal=signal_snapshot.electricity_demand_signal,
        signal_lines=_format_signals(signal_snapshot),
        regimes=", ".join(r.replace("_", " ").upper() for r in macro_regime.regimes),
        regime_rationale=regime_rationale_str,
        stance=portfolio.stance.upper(),
        engine_breakdown=_format_engines(portfolio),
        portfolio_rationale=portfolio.rationale,
        gov_status="PASSED ✓" if governance.passed else f"FAILED — {len(governance.violations)} violation(s)",
        governance_detail=_format_violations(governance),
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"  [Stage 7] Claude prompt saved → {PROMPT_PATH}")
    return prompt
