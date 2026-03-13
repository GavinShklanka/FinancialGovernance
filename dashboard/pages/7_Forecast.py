import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid

st.set_page_config(page_title="Forecast | Lumin Finance", page_icon="◎", layout="wide")
apply_global_styles()

page_hero(
    kicker="Forward Outlook",
    title="What might happen next?",
    subtitle="The forecast engine analyzes historical signal snapshots to compute regime transition probabilities. These probabilities indicate the likelihood of macro regime changes in the coming cycle.",
    chips=["Regime Transitions", "Signal History", "Probability Engine"],
)

section_divider("Regime Transition Probabilities")

# Load forecast data
try:
    from app.forecast_engine import compute_regime_forecast
    forecast = compute_regime_forecast()

    if forecast and isinstance(forecast, dict):
        prob_cards = []
        for regime_name, probability in forecast.items():
            if isinstance(probability, (int, float)):
                pct = probability * 100 if probability <= 1 else probability
                tone_icon = "▲" if pct > 50 else "●" if pct > 25 else "▼"
                prob_cards.append({
                    "eyebrow": f"{pct:.0f}% Probability",
                    "title": f"{tone_icon} {regime_name.replace('_', ' ').title()}",
                    "body": f"Historical signal patterns suggest {'high' if pct > 50 else 'moderate' if pct > 25 else 'low'} likelihood of this regime emerging.",
                    "icon": "◎",
                })
        if prob_cards:
            card_grid(prob_cards, columns=3)
        else:
            analyst_note("Insufficient Data", "Not enough historical snapshots to compute probabilities.", tone="warning")
    else:
        analyst_note("Forecast Unavailable", "The forecast engine returned no regime probabilities. Accumulate more weekly pipeline runs.", tone="warning")
except Exception as e:
    analyst_note("Forecast Engine Error", f"Could not compute forecast: {str(e)}", tone="warning")

section_divider("Historical Context")

# Show available history
history_dir = os.path.join(ROOT_DIR, "data", "history", "signals")
if os.path.exists(history_dir):
    snapshots = sorted([f for f in os.listdir(history_dir) if f.endswith(".json")])
    if snapshots:
        analyst_note(
            f"{len(snapshots)} Historical Snapshot(s) Available",
            "The forecast engine uses these snapshots to compute regime transition frequencies. More snapshots improve probability accuracy.",
            tone="success",
        )
        for snap in snapshots[-5:]:
            date = snap.replace("signal_snapshot_", "").replace(".json", "").replace("_", "-")
            st.markdown(f"• **{date}**")
    else:
        analyst_note("No History", "Run multiple pipeline cycles to build signal history for forecasting.", tone="warning")
else:
    analyst_note("History Directory Missing", "Run at least one pipeline cycle to initialize the historical data store.", tone="warning")
