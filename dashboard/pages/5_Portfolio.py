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

portfolio_data = load_portfolio()
engines = portfolio_data.get("engines", [])
cash_pct = portfolio_data.get("cash_pct", 0)

if not engines:
    st.info("No portfolio allocation models found.")
else:
    col1, col2 = st.columns([1, 1])

    with col1:
        # Build pie chart data natively
        names = [e["name"] for e in engines]
        values = [e["allocation_pct"] for e in engines]
        if cash_pct > 0:
            names.append("Cash")
            values.append(cash_pct)
            
        df_port = pd.DataFrame({"Engine": names, "Allocation": values})
        fig_pie = px.pie(df_port, names="Engine", values="Allocation", hole=0.4, title="Active Model Allocation")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown(f"### Overall Rationale")
        st.markdown(f"<p class='explanation-text'>{portfolio_data.get('overall_rationale')}</p>", unsafe_allow_html=True)
        st.markdown(f"**Current Stance:** {portfolio_data.get('stance', 'Unknown').upper()}")
        st.divider()
        
        st.markdown("### Specific Engine Strategies")
        for engine in engines:
            st.markdown(f"#### {engine['name']}")
            st.markdown(f"**Weight:** {engine['allocation_pct']*100:.0f}%")
            st.markdown(f"*{engine['rationale']}*")
            st.markdown("<br>", unsafe_allow_html=True)
