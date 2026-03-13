import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_regime, load_signals, load_portfolio, load_alerts

st.set_page_config(page_title="Lumin Finance", page_icon="◈", layout="wide")
apply_global_styles()

page_hero(
    kicker="Lumin Finance / AI Macro Intelligence",
    title="Macro narratives, priced like a live research desk.",
    subtitle="Institutional dark-mode terminal with cinematic flow, glass surfaces, and live evidence framing across the full seven-page architecture.",
    chips=["Discover", "Signals", "Ecosystems", "Company", "Portfolio", "Monitor", "Forecast"],
)

section_divider("System Overview")

regime = load_regime()
signals = load_signals().get("signals", [])
portfolio = load_portfolio()
alerts_data = load_alerts().get("alerts", [])

overview_cards = [
    {
        "eyebrow": "Active Regime",
        "title": regime.get("active_regime", "Unknown"),
        "body": "The macro environment currently detected by the regime engine.",
        "icon": "◈",
    },
    {
        "eyebrow": "Signal Count",
        "title": f"{len(signals)} Active Signals",
        "body": f"Aggregate score driving portfolio stance and regime classification.",
        "icon": "◎",
    },
    {
        "eyebrow": "Portfolio Stance",
        "title": portfolio.get("stance", "neutral").upper(),
        "body": f"Cash reserve: {portfolio.get('cash_pct', 0) * 100:.0f}%",
        "icon": "▲",
    },
]

card_grid(overview_cards, columns=3)

if alerts_data:
    section_divider("Active Alerts")
    for alert in alerts_data:
        tone = "danger" if alert["severity"] == "high" else "warning"
        analyst_note(alert["severity"].upper(), alert["message"], tone=tone)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Navigate using the sidebar to explore: Discover → Signals → Ecosystems → Company → Portfolio → Monitor → Forecast")
