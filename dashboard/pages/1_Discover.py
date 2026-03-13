import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_regime, load_signals

st.set_page_config(page_title="Discover | Lumin Finance", page_icon="◈", layout="wide")
apply_global_styles()

regime = load_regime()
signals_data = load_signals().get("signals", [])

active = regime.get("active_regime", "Unknown")

# Build signal chip list for the hero
signal_chips = []
for s in signals_data[:6]:
    prefix = "▲" if s["score"] > 0 else "▼" if s["score"] < 0 else "●"
    signal_chips.append(f"{prefix} {s['name']} ({s['score']:+.1f})")

page_hero(
    kicker="The World Right Now",
    title=active,
    subtitle="This is the macro regime currently detected by the Antigravity signal engine. The regime classification determines how capital is allocated across growth, infrastructure, and defensive strategies.",
    chips=signal_chips if signal_chips else ["No active signals"],
)

section_divider("Why This Regime Is Active")

# Rationale from regime_snapshot
rationale = regime.get("rationale", {})
if isinstance(rationale, dict) and rationale:
    rationale_cards = []
    for regime_name, reason in rationale.items():
        rationale_cards.append({
            "eyebrow": "Regime Driver",
            "title": regime_name.replace("_", " ").title(),
            "body": reason,
            "icon": "◈",
        })
    card_grid(rationale_cards, columns=2)
else:
    # Fallback: build explanation from signal data
    bullish = [s for s in signals_data if s["score"] > 0]
    bearish = [s for s in signals_data if s["score"] < 0]

    if bullish:
        analyst_note(
            "Expansion Signals",
            " • ".join([f"{s['name']} ({s['score']:+.2f})" for s in bullish]),
            tone="success",
        )
    if bearish:
        analyst_note(
            "Contraction Signals",
            " • ".join([f"{s['name']} ({s['score']:+.2f})" for s in bearish]),
            tone="danger",
        )

section_divider("Signal Drivers Summary")

if signals_data:
    driver_cards = []
    for sig in signals_data:
        tone_icon = "▲" if sig["score"] > 0 else "▼" if sig["score"] < 0 else "●"
        driver_cards.append({
            "eyebrow": f"Score: {sig['score']:+.2f}",
            "title": f"{tone_icon} {sig['name']}",
            "body": sig.get("explanation", "Signal explanation pending."),
            "icon": "◎",
        })
    card_grid(driver_cards, columns=3)

# Regime history timeline
history = regime.get("history", [])
if history:
    section_divider("Regime Timeline")
    for entry in history[-5:]:
        st.markdown(f"**{entry['date']}** → {entry['regime']}")
