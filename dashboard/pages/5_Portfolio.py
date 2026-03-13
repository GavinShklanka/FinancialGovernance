import streamlit as st
import os, sys
import plotly.express as px
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css
from app.ui.data_bridge import load_portfolio

st.set_page_config(page_title="Portfolio Builder | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("How should capital be allocated?")
st.markdown("<p class='explanation-text'>Portfolio Builder & Strategy Allocation</p>", unsafe_allow_html=True)
st.divider()

portfolio_weights = load_portfolio().get("weights", {"AI Infrastructure": 0.4, "Defense": 0.3, "Cash": 0.3})

col1, col2 = st.columns([1, 1])

with col1:
    df_port = pd.DataFrame(list(portfolio_weights.items()), columns=["Engine", "Allocation"])
    fig_pie = px.pie(df_port, names="Engine", values="Allocation", hole=0.4, title="Recommended Allocation")
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("### Allocation Explanations")
    for key, val in portfolio_weights.items():
        st.markdown(f"#### {key} Allocation")
        st.markdown(f"Weight: **{val*100:.0f}%**")
        st.markdown("High allocation due to dominant position and strong demand signals aligned with the active macro regime.")
