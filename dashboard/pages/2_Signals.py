import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css
from app.ui.data_bridge import load_signals

st.set_page_config(page_title="Signals | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("What evidence is driving this conclusion?")
st.markdown("<p class='explanation-text'>Signal Intelligence Panel</p>", unsafe_allow_html=True)
st.divider()

signals_data = load_signals().get("signals", [])

if not signals_data:
    st.info("No signal data available.")
else:
    for sig in signals_data:
        st.markdown(f"### {sig['name']}")
        score_color = "#22C55E" if sig['score'] > 0 else "#EF4444" if sig['score'] < 0 else "#F59E0B"
        st.markdown(f"**Score:** <span style='color:{score_color}; font-weight:bold;'>{sig['score']:+.2f}</span>", unsafe_allow_html=True)
        st.markdown("**Explanation:**")
        exp = sig.get('explanation')
        if exp:
            st.markdown(f"{exp}")
        else:
            st.markdown("*Historically predictable patterns suggest expansion parameters or critical contraction markers.*")
        st.divider()
