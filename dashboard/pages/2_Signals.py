import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_signals

st.set_page_config(page_title="Signals | Lumin Finance", page_icon="◎", layout="wide")
apply_global_styles()

signals_data = load_signals().get("signals", [])

total_score = sum(s["score"] for s in signals_data) if signals_data else 0
bullish_count = sum(1 for s in signals_data if s["score"] > 0)
bearish_count = sum(1 for s in signals_data if s["score"] < 0)

page_hero(
    kicker="Evidence Layer",
    title="Signal Intelligence",
    subtitle="Each signal below represents a measurable macro variable scored by the Antigravity engine. Positive scores indicate expansion. Negative scores indicate contraction. Every signal includes an analyst-grade explanation of its economic meaning.",
    chips=[f"Total: {total_score:+.2f}", f"▲ {bullish_count} Bullish", f"▼ {bearish_count} Bearish"],
)

section_divider("Active Signals")

if not signals_data:
    st.info("No signal data available. Run the pipeline.")
else:
    for sig in signals_data:
        tone = "success" if sig["score"] > 0 else "danger" if sig["score"] < 0 else "warning"
        prefix = "▲" if sig["score"] > 0 else "▼" if sig["score"] < 0 else "●"
        
        exp = sig.get("explanation", "")
        if not exp:
            exp = "Historically predictable patterns suggest expansion parameters or critical contraction markers based on real-time data flow."

        analyst_note(
            f"{prefix} {sig['name']} — Score: {sig['score']:+.2f}",
            exp,
            tone=tone,
        )
