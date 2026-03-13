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
ANTIGRAVITY — CLAUDE RESEARCH BRIEFING REQUEST
Generated: {timestamp}
================================================================================

You are acting as a senior macro investment research analyst.

Below is this week's full Antigravity pipeline output. Your task is to:
  1. Evaluate the macro regime and signal data
  2. Critique the portfolio recommendation
  3. Identify the 2–3 highest-conviction investment themes
  4. Flag any risks or contradictions in the signal picture
  5. Provide 1–2 historical analogues for the current regime
  6. Give a brief recommendation: Hold / Rebalance / Increase / Reduce exposure

Be direct, concise, and institution-grade in your analysis.

────────────────────────────────────────────────────────────────────────────────
SECTION 1 — MACRO SIGNAL SNAPSHOT
────────────────────────────────────────────────────────────────────────────────

Timestamp   : {timestamp}
Total Score : {total_score:+.2f}  (scale: heavily weighted sum; >5 = strong bull, <-5 = strong bear)

Core Market Data:
  SPY:       ${spy_price:,.2f}
  VIX:       {vix}
  DXY:       {dxy}
  10Y Yield: {tnx_yield}%
  Gold:      ${gold_price:,.2f}
  BTC:       ${btc_price:,.0f}

Extended Signals:
  Copper Inventories:       {copper_inventories} kt
  Uranium Spot:             ${uranium_spot}/lb
  SEMI Equipment Orders:    +{semi_equipment_orders}% YoY
  Hyperscaler Capex Signal: {hyperscaler_capex_signal}/10
  Cyber Incidents (weekly): {cyber_incidents:.0f}
  China PMI:                {china_pmi}
  Electricity Demand:       +{electricity_demand_signal}% YoY

Signal Scores:
{signal_lines}

────────────────────────────────────────────────────────────────────────────────
SECTION 2 — MACRO REGIME CLASSIFICATION
────────────────────────────────────────────────────────────────────────────────

Active Regimes: {regimes}

Regime Analysis:
{regime_rationale}

────────────────────────────────────────────────────────────────────────────────
SECTION 3 — PORTFOLIO RECOMMENDATION (Three-Engine Model)
────────────────────────────────────────────────────────────────────────────────

Stance: {stance}

{engine_breakdown}

Portfolio Rationale: {portfolio_rationale}

────────────────────────────────────────────────────────────────────────────────
SECTION 4 — GOVERNANCE & RISK FLAGS
────────────────────────────────────────────────────────────────────────────────

Governance Status: {gov_status}

{governance_detail}

────────────────────────────────────────────────────────────────────────────────
YOUR ANALYSIS (Claude)
────────────────────────────────────────────────────────────────────────────────

Please structure your response as follows:

**1. Macro Regime Assessment**
[Your read on the regime — agree / disagree with classification?]

**2. Signal Strength Evaluation**
[Which signals are most reliable? Which are contradictory?]

**3. Portfolio Critique**
[Does the three-engine allocation make sense? What would you change?]

**4. Top 2–3 Investment Themes**
[Specific, actionable thematic ideas based on this regime]

**5. Key Risks**
[What could break this thesis?]

**6. Historical Analogues**
[What past macro environment does this resemble?]

**7. Recommendation**
[Hold / Rebalance / Increase / Reduce — which specific engines and why]

================================================================================
END OF ANTIGRAVITY BRIEFING
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
