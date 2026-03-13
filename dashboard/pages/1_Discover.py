import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css
from app.ui.data_bridge import load_regime

st.set_page_config(page_title="Discover | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("What is happening in the world right now?")
st.markdown("<p class='explanation-text'>Global Macro Context</p>", unsafe_allow_html=True)
st.divider()

regime_data = load_regime()
current_regime = regime_data.get("active_regime", "Unknown")

st.markdown("### ACTIVE MACRO REGIME")
st.markdown(f"<div class='metric-value'>{current_regime}</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("#### Why this regime is active:")
rationale = regime_data.get("regime_rationale", {})
if rationale:
    for k, v in rationale.items():
        st.markdown(f"• **{k.replace('_', ' ').title()}**: {v}")
else:
    # Fallback to the user's hardcoded example if no data to prove the concept works
    st.markdown("""
    • Semiconductor demand accelerating
    • Hyperscaler AI capex increasing
    • Cyber incidents rising
    • Copper demand signaling infrastructure expansion
    """)
