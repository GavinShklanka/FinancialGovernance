import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_alerts, load_governance, load_portfolio_evaluation

st.set_page_config(page_title="Monitor | Lumin Finance", page_icon="▲", layout="wide")
apply_global_styles()

alerts_data = load_alerts().get("alerts", [])
governance = load_governance()
eval_data = load_portfolio_evaluation()

high_alerts = [a for a in alerts_data if a["severity"] == "high"]
medium_alerts = [a for a in alerts_data if a["severity"] == "medium"]

page_hero(
    kicker="Risk Monitoring",
    title="What could break the thesis?",
    subtitle="The monitor surfaces alerts, governance constraint checks, evaluation status, and risk signals that could invalidate the current macro positioning.",
    chips=[f"🔴 {len(high_alerts)} Critical", f"🟡 {len(medium_alerts)} Warning", f"Governance: {governance['status'].upper()}"],
)

# ── Active Alerts ────────────────────────────────────────────────────────────
section_divider("Active Alerts")

if not alerts_data:
    analyst_note("No Active Alerts", "The system has no material risk signals at this time.", tone="success")
else:
    for alert in alerts_data:
        tone = "danger" if alert["severity"] == "high" else "warning"
        analyst_note(
            f"{'🔴 CRITICAL' if alert['severity'] == 'high' else '🟡 WARNING'}",
            alert["message"],
            tone=tone,
        )

# ── Governance & Compliance ──────────────────────────────────────────────────
section_divider("Governance & Compliance")

gov_status = governance.get("status", "unknown")
violations = governance.get("violations", [])

if gov_status == "passed":
    analyst_note(
        "✓ GOVERNANCE CHECKS PASSED",
        "Portfolio engine complies with all defined risk and position limits.",
        tone="success",
    )
else:
    analyst_note(
        "✗ GOVERNANCE CHECKS FAILED",
        f"{len(violations)} violation(s) detected. Review before execution.",
        tone="danger",
    )

    if violations:
        violation_cards = []
        for v in violations:
            if isinstance(v, dict):
                violation_cards.append({
                    "eyebrow": v.get("severity", "WARNING"),
                    "title": v.get("rule", "Unknown Rule"),
                    "body": v.get("detail", "No detail provided."),
                    "icon": "⚠",
                })
            else:
                violation_cards.append({
                    "eyebrow": "VIOLATION",
                    "title": str(v),
                    "body": "",
                    "icon": "⚠",
                })
        card_grid(violation_cards, columns=2)

# ── Evaluation Summary Widget ────────────────────────────────────────────────
section_divider("Evaluation Status")

if eval_data:
    eval_cards = []

    # Count decisions by type
    decisions = eval_data.get("decisions", [])
    buy_count = sum(1 for d in decisions if d.get("action") == "BUY_NOW")
    scale_count = sum(1 for d in decisions if d.get("action") == "SCALE_IN")
    hold_count = sum(1 for d in decisions if d.get("action") == "HOLD")
    trim_count = sum(1 for d in decisions if d.get("action") in ("TRIM", "EXIT"))

    eval_cards.append({
        "eyebrow": "REGIME",
        "title": eval_data.get("regime", "Unknown"),
        "body": f"Signal score: {eval_data.get('total_signal_score', 0):+.2f}",
        "icon": "◎",
    })
    eval_cards.append({
        "eyebrow": "DECISIONS",
        "title": f"{buy_count} Buy · {scale_count} Scale · {hold_count} Hold · {trim_count} Trim",
        "body": eval_data.get("simple_summary", ""),
        "icon": "◈",
    })
    eval_cards.append({
        "eyebrow": "GOVERNANCE",
        "title": "Passed ✓" if eval_data.get("governance_passed") else "Failed ✗",
        "body": f"Report ID: {eval_data.get('report_id', 'N/A')}",
        "icon": "▲" if eval_data.get("governance_passed") else "⚠",
    })

    card_grid(eval_cards, columns=3)

    # Trim/Exit alerts
    trim_decisions = [d for d in decisions if d.get("action") in ("TRIM", "EXIT")]
    if trim_decisions:
        section_divider("⚠ Positions Flagged for Reduction")
        for d in trim_decisions:
            analyst_note(
                f"{d['ticker']} — {d['action']}",
                f"Reason: {d.get('primary_risk', 'Regime not supportive.')} "
                f"Invalidation: {d.get('invalidation_trigger', 'N/A')}",
                tone="danger",
            )
else:
    analyst_note(
        "No Evaluation Report",
        "Run the pipeline to generate portfolio evaluation data.",
        tone="warning",
    )
