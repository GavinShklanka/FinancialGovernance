import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_alerts, load_governance

st.set_page_config(page_title="Monitor | Lumin Finance", page_icon="▲", layout="wide")
apply_global_styles()

alerts_data = load_alerts().get("alerts", [])
governance = load_governance()

high_alerts = [a for a in alerts_data if a["severity"] == "high"]
medium_alerts = [a for a in alerts_data if a["severity"] == "medium"]

page_hero(
    kicker="Risk Monitoring",
    title="What could break the thesis?",
    subtitle="The monitor surfaces alerts, governance constraint checks, and risk signals that could invalidate the current macro positioning. If governance fails, the portfolio engine adjusts automatically.",
    chips=[f"🔴 {len(high_alerts)} Critical", f"🟡 {len(medium_alerts)} Warning", f"Governance: {governance['status'].upper()}"],
)

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
