"""
Antigravity — Report generation engine (Stage 8 upgrade).

Renders a comprehensive Markdown weekly investment report covering
all 8 pipeline stages. Includes macro regime, three-engine portfolio,
governance results, and Claude prompt pointer.
"""

import os
from datetime import datetime, timezone

from app.models import SignalSnapshot, MacroRegime, Portfolio, GovernanceResult


OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "outputs"
)
REPORT_PATH = os.path.join(OUTPUT_DIR, "weekly_report.md")


def generate_report(
    signal_snapshot: SignalSnapshot,
    portfolio: Portfolio,
    macro_regime: MacroRegime,
    governance: GovernanceResult,
    education_notes: list | None = None,
) -> str:
    """Assemble the full Markdown weekly report from all pipeline outputs."""

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Header ────────────────────────────────────────────────────
    lines = [
        "# 🛰 Antigravity Weekly Investment Report",
        "",
        f"**Generated:** {now_str}  ",
        f"**Pipeline Cycle:** Full 8-Stage Run  ",
        f"**Overall Stance:** `{portfolio.stance.upper()}`",
        "",
        "---",
    ]

    # ── Stage 1: Market Snapshot ──────────────────────────────────
    lines += [
        "",
        "## Stage 1 — Market Snapshot",
        "",
        "| Indicator | Value |",
        "|-----------|-------|",
        f"| SPY | ${signal_snapshot.spy_price:,.2f} |",
        f"| VIX | {signal_snapshot.vix} |",
        f"| DXY | {signal_snapshot.dxy} |",
        f"| 10Y Yield | {signal_snapshot.tnx_yield}% |",
        f"| Gold | ${signal_snapshot.gold_price:,.2f} |",
        f"| BTC | ${signal_snapshot.btc_price:,.0f} |",
        "",
        "**Extended Signals:**",
        "",
        "| Signal | Value |",
        "|--------|-------|",
        f"| Copper Inventories | {signal_snapshot.copper_inventories} kt |",
        f"| Uranium Spot | ${signal_snapshot.uranium_spot}/lb |",
        f"| SEMI Equipment Orders | +{signal_snapshot.semi_equipment_orders}% YoY |",
        f"| Hyperscaler Capex Signal | {signal_snapshot.hyperscaler_capex_signal}/10 |",
        f"| Cyber Incidents (weekly) | {signal_snapshot.cyber_incidents:.0f} |",
        f"| China PMI | {signal_snapshot.china_pmi} |",
        f"| Electricity Demand | +{signal_snapshot.electricity_demand_signal}% YoY |",
        "",
        "---",
    ]

    # ── Stage 2: Signal Scores ────────────────────────────────────
    lines += [
        "",
        "## Stage 2 — Signal Scores",
        "",
        f"**Total Weighted Score:** `{signal_snapshot.total_score:+.2f}`",
        "",
        "| Signal | Value | Score | Weight | Explanation |",
        "|--------|-------|-------|--------|-------------|",
    ]
    for s in signal_snapshot.signals:
        arrow = "▲" if s.score > 0 else ("▼" if s.score < 0 else "●")
        lines.append(
            f"| {s.name} | {s.value} | {arrow} {s.score:+.1f} | {s.weight} | {s.explanation} |"
        )

    lines += ["", "---"]

    # ── Stage 3: Macro Regime ─────────────────────────────────────
    regime_display = ", ".join(
        f"`{r.replace('_', ' ').upper()}`" for r in macro_regime.regimes
    )
    lines += [
        "",
        "## Stage 3 — Macro Regime",
        "",
        f"**Active Regimes:** {regime_display}",
        "",
    ]
    for regime_key, rationale in macro_regime.regime_rationale.items():
        lines.append(f"**{regime_key.replace('_', ' ').title()}:** {rationale}")
        lines.append("")

    lines += ["---"]

    # ── Stage 4: Portfolio — Three-Engine Model ───────────────────
    lines += [
        "",
        "## Stage 4 — Portfolio Recommendation (Three-Engine Model)",
        "",
        f"**Stance:** `{portfolio.stance.upper()}`  ",
        f"**Cash:** `{portfolio.cash_pct:.0%}`",
        "",
    ]
    for engine in portfolio.engines:
        lines += [
            f"### {engine.name} — `{engine.allocation_pct:.0%}`",
            "",
            f"**Holdings:** {', '.join(engine.holdings)}",
            "",
            f"**Rationale:** {engine.rationale}",
            "",
        ]

    lines += [
        f"> {portfolio.rationale}",
        "",
        "---",
    ]

    # ── Stage 5: Governance ───────────────────────────────────────
    gov_badge = "✅ PASSED" if governance.passed else f"⚠️ FAILED ({len(governance.violations)} violation(s))"
    lines += [
        "",
        "## Stage 5 — Governance & Policy Check",
        "",
        f"**Status:** {gov_badge}",
        "",
    ]
    if governance.violations:
        lines.append("| Severity | Rule | Detail |")
        lines.append("|----------|------|--------|")
        for v in governance.violations:
            lines.append(f"| `{v.severity}` | {v.rule} | {v.detail} |")
        lines.append("")
    for note in governance.notes:
        lines.append(f"> {note}")
    lines += ["", "---"]

    # ── Stage 6: Decision Graph ───────────────────────────────────
    lines += [
        "",
        "## Stage 6 — Decision Graph",
        "",
        "This cycle's reasoning chain has been recorded in `decision_graph.json`.",
        "",
        "```",
        "Signal Node → Regime Node → Portfolio Node → Governance Node → Human Approval Node",
        "```",
        "",
        "---",
    ]

    # ── Stage 7: Claude Prompt ────────────────────────────────────
    lines += [
        "",
        "## Stage 7 — AI Research Layer (Claude)",
        "",
        "Your Claude master prompt has been generated at:",
        "",
        "```",
        "app/outputs/claude_prompt.txt",
        "```",
        "",
        "**Instructions:**",
        "1. Open `claude_prompt.txt`",
        "2. Copy the entire contents",
        "3. Paste into Claude (claude.ai or API)",
        "4. Receive your structured research briefing",
        "",
        "---",
    ]

    # ── Stage 8: Human Decision ───────────────────────────────────
    lines += [
        "",
        "## Stage 8 — Human Decision",
        "",
        "After reviewing the Claude briefing, choose one of:",
        "",
        "| Decision | Trigger |",
        "|----------|---------|",
        "| **Hold** | Signals unchanged, regime stable |",
        "| **Rebalance** | Regime shifted, engines misaligned |",
        "| **Increase Exposure** | Score strongly bullish, regime confirmed |",
        "| **Reduce Exposure** | Governance flag, VIX spike, or bearish regime |",
        "",
        "Execution occurs manually in **Wealthsimple TFSA**.",
        "",
        "---",
    ]

    # ── Education Notes ───────────────────────────────────────────
    if education_notes:
        lines += [
            "",
            "## Education Notes",
            "",
        ]
        for note in education_notes:
            lines.append(f"- {note}")
        lines.append("")
        lines += ["---"]

    # ── Weekly Cadence ────────────────────────────────────────────
    lines += [
        "",
        "## Weekly Operating Cadence",
        "",
        "| Day | Action |",
        "|-----|--------|",
        "| **Monday** | Run `python antigravity/run_antigravity_cycle.py` |",
        "| **Tuesday** | Paste `claude_prompt.txt` into Claude, interpret briefing |",
        "| **Wednesday** | Research Fed policy, commodity trends, AI capex news |",
        "| **Thursday** | Adjust allocations if regime or signals have shifted |",
        "| **Friday** | Log decision — update investment journal + decision graph |",
        "",
        "---",
        "",
        "*Report generated by the Antigravity Macro Investment Intelligence Engine.*",
    ]

    return "\n".join(lines)


def save_report(report: str) -> None:
    """Write the Markdown report to app/outputs/weekly_report.md."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  [Stage 8] Weekly report saved → {REPORT_PATH}")
