import streamlit as st
import plotly.express as px
import pandas as pd
import os
import sys

# Ensure root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.data_bridge import (
    load_signals,
    load_regime,
    load_portfolio,
    load_alerts,
    load_governance
)

from replay.replay_engine import replay_pipeline

st.set_page_config(
    page_title="Antigravity Macro Terminal",
    layout="wide"
)

st.title("Antigravity Macro Intelligence Terminal")

regime = load_regime()
current_regime = regime.get("active_regime", "Unknown")

st.markdown(
f"""
## Active Macro Regime  
**{current_regime}**
"""
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Signal Heatmap")
    signals = load_signals().get("signals", {})
    if signals:
        df = pd.DataFrame(
            signals.items(),
            columns=["Signal","Score"]
        )
        fig = px.imshow(
            [df["Score"]],
            x=df["Signal"],
            y=["Signals"],
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Portfolio Allocation")
    portfolio = load_portfolio().get("weights", {})
    if portfolio:
        fig = px.pie(
            names=list(portfolio.keys()),
            values=list(portfolio.values())
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Macro Regime Timeline")
regime_history = load_regime().get("history", [])
if regime_history:
    df = pd.DataFrame(regime_history)
    fig = px.line(
        df,
        x="date",
        y="regime"
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Risk Alerts")
alerts = load_alerts().get("alerts", [])
if alerts:
    for alert in alerts:
        severity = alert.get("severity","info")
        if severity == "high":
            st.error(alert["message"])
        elif severity == "medium":
            st.warning(alert["message"])
        else:
            st.info(alert["message"])
else:
    st.success("No active critical risk alerts.")

st.subheader("Governance Check")
gov = load_governance()
if gov.get("status") == "passed":
    st.success("Governance Check PASSED")
else:
    st.error("Governance Check FAILED")

st.subheader("Historical Replay Lab")
# Populate dates dynamically if available
history_dirs = []
state_dir = os.path.join(ROOT_DIR, "state", "versions")
if os.path.exists(state_dir):
    history_dirs = sorted([d for d in os.listdir(state_dir) if os.path.isdir(os.path.join(state_dir, d))], reverse=True)

date = st.selectbox(
    "Select Historical Week",
    history_dirs if history_dirs else ["2026_03_13"]
)

strategy = st.selectbox(
    "Alternative Strategy",
    [
        "default",
        "defensive_regime",
        "ai_infrastructure_boom"
    ]
)

if st.button("Run Replay"):
    strat_arg = strategy if strategy != "default" else None
    result = replay_pipeline(date, strat_arg)
    
    if result and "original" in result and "alternative" in result:
        original = result["original"]
        alt = result["alternative"]

        comparison_df = pd.DataFrame({
            "Original": original,
            "Alternative": alt
        })

        st.bar_chart(comparison_df)
    else:
        st.warning("Replay completed, but dictionary response was not returned. Check terminal for output.")

st.divider()

st.caption("Signals drive regime detection and portfolio allocation.")

st.subheader("Regime Forecast")
forecast = {
    "AI Infrastructure Boom":0.63,
    "Defensive Regime":0.22,
    "Liquidity Expansion":0.15
}
df_forecast = pd.DataFrame(
    forecast.items(),
    columns=["Regime","Probability"]
)
fig_forecast = px.bar(
    df_forecast,
    x="Regime",
    y="Probability"
)
st.plotly_chart(fig_forecast)
