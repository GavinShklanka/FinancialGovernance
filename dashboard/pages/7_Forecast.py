import streamlit as st
import os, sys
import pandas as pd
import plotly.express as px

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css
from app.forecast_engine import generate_forecast

st.set_page_config(page_title="Forecast | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("What might happen next?")
st.markdown("<p class='explanation-text'>Signal Forecast Engine</p>", unsafe_allow_html=True)
st.divider()

forecast_data = generate_forecast()
if forecast_data:
    df_fc = pd.DataFrame(forecast_data)
    fig_fc = px.bar(
        df_fc, x="Regime", y="Probability", title="Next Regime Probabilities", 
        color="Probability", color_continuous_scale="Blues", text_auto=".1%"
    )
    fig_fc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    fig_fc.update_yaxes(tickformat=".0%")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_fc, use_container_width=True)
    with col2:
        st.markdown("### Explanation")
        st.markdown("Based on historical signal patterns and structural momentum, the current regime has the highest probability of persisting over the next quarter.")
        for item in forecast_data:
            st.markdown(f"**{item['Regime']}**: {item['Probability']*100:.0f}% chance.")
else:
    st.warning("No forecast data available.")
