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
from app.forecast_engine import generate_forecast
from replay.replay_engine import replay_pipeline

# Configure page
st.set_page_config(
    page_title="Lumin Finance Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Lumin Finance Aesthetic
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
        color: white;
    }
    .css-1d391kg {
        background-color: transparent !important;
    }
    div[data-testid="stVerticalBlock"] > div > div {
        background: rgba(17, 24, 39, 0.9); /* #111827 panel color */
        border-radius: 12px;
        padding: 5px;
    }
    h1, h2, h3, h4 {
        color: #38BDF8 !important; /* accent */
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #38BDF8; /* accent */
    }
    .success-text { color: #22C55E; font-weight: bold; } /* success */
    .warning-text { color: #F59E0B; font-weight: bold; } /* warning */
    .danger-text { color: #EF4444; font-weight: bold; } /* danger */
    .explanation-text {
        font-size: 14px;
        color: #94A3B8;
        font-style: italic;
    }
    /* Simple divider override */
    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("Lumin Finance")
st.markdown("*AI Macro Intelligence Terminal*")
st.divider()

# Load Data
signals_data = load_signals().get("signals", [])
regime_data = load_regime()
portfolio_data = load_portfolio().get("weights", {})
alerts = load_alerts().get("alerts", [])

# ==============================================================================
# SECTION 1: THE WORLD RIGHT NOW (Macro Regime)
# ==============================================================================
st.header("1. The World Right Now")
st.markdown("<p class='explanation-text'>Explaining the current macro environment based on high-frequency signals.</p>", unsafe_allow_html=True)

col1_a, col1_b = st.columns([1, 2])
current_regime = regime_data.get("active_regime", "Unknown")

with col1_a:
    st.markdown("### Active Macro Regime")
    st.markdown(f"<div class='metric-value'>{current_regime}</div>", unsafe_allow_html=True)

with col1_b:
    st.markdown("### Why the model believes this:")
    rationale = regime_data.get("regime_rationale", {})
    if rationale:
        for k, v in rationale.items():
            st.markdown(f"**{k.replace('_', ' ').title()}**: {v}")
    else:
        st.write("No dominant regime driver detected.")

st.divider()

# ==============================================================================
# SECTION 2: WHAT THE SIGNALS ARE SAYING (Evidence Layer)
# ==============================================================================
st.header("2. What The Signals Are Saying")
st.markdown("<p class='explanation-text'>The Evidence Layer: Visualizing the underlying economic indicators driving the regime.</p>", unsafe_allow_html=True)

if signals_data:
    # Convert list of dicts to DataFrame for Plotly
    df_sig = pd.DataFrame(signals_data)
    # We want a heatmap: x=Signals, y=dummy, color=score, hover=explanation
    fig_sig = px.imshow(
        [df_sig["score"]],
        x=df_sig["name"],
        y=["Signal Strength"],
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    
    # Custom hover data in Plotly express imshow is tricky, let's use a Bar chart instead for better tooltips
    fig_bar = px.bar(
        df_sig,
        y="name",
        x="score",
        orientation='h',
        color="score",
        color_continuous_scale="RdYlGn",
        hover_data=["explanation"],
        title="Signal Strengths & Economic Meaning"
    )
    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No signal data available.")

st.divider()

# ==============================================================================
# SECTION 3: WHAT THE MODEL THINKS HAPPENS NEXT
# ==============================================================================
st.header("3. What The Model Thinks Happens Next")
st.markdown("<p class='explanation-text'>The Regime Forecast Engine computes transition probabilities based on historical signal persistence.</p>", unsafe_allow_html=True)

forecast_data = generate_forecast()
if forecast_data:
    df_fc = pd.DataFrame(forecast_data)
    fig_fc = px.bar(
        df_fc,
        x="Regime",
        y="Probability",
        title="Next Regime Probabilities",
        color="Probability",
        color_continuous_scale="Blues"
    )
    fig_fc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    fig_fc.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_fc, use_container_width=True)

st.divider()

# ==============================================================================
# SECTION 4: CAPITAL ALLOCATION STRATEGY
# ==============================================================================
st.header("4. Capital Allocation Strategy")
st.markdown("<p class='explanation-text'>Where should capital go? The system shifts allocations dynamically while maintaining governance.</p>", unsafe_allow_html=True)

if portfolio_data:
    col4_a, col4_b = st.columns([1, 1])
    with col4_a:
        fig_pie = px.pie(
            names=list(portfolio_data.keys()),
            values=list(portfolio_data.values()),
            hole=0.4
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col4_b:
        st.markdown("### Strategic Rationale")
        st.markdown("""
        The system allocates capital across these engines because:
        * **AI Infrastructure / Growth**: Captures upside in semiconductor demand and hyperscaler capex.
        * **Defense / Cash**: Preserves capital against liquidity contraction risks and VIX spikes.
        """)
        gov = load_governance()
        if gov.get("status") == "passed":
            st.markdown("<p class='success-text'>✓ Governance Check PASSED: Allocation complies with risk limits.</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='danger-text'>⚠ Governance Check FAILED: Allocation violates risk parameters.</p>", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# SECTION 5: RISK MONITORING
# ==============================================================================
st.header("5. Risk Monitoring")
st.markdown("<p class='explanation-text'>Highlighting signals that could invalidate the thesis or cause structural damage.</p>", unsafe_allow_html=True)

if alerts:
    for alert in alerts:
        severity = alert.get("severity", "info")
        msg = alert.get("message", "")
        if severity == "high":
            st.error(f"⚠ CRITICAL RISK: {msg}")
        elif severity == "medium":
            st.warning(f"⚠ ELEVATED RISK: {msg}")
        else:
            st.info(msg)
else:
    st.markdown("<p class='success-text'>No severe macro risks currently detected by the Alert Engine.</p>", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# SECTION 6: HISTORICAL REPLAY LAB / STRATEGY SIMULATOR
# ==============================================================================
st.header("6. Historical Replay Lab")
st.markdown("<p class='explanation-text'>Macro Strategy Simulator: How would the portfolio perform if the regime abruptly shifted?</p>", unsafe_allow_html=True)

history_dirs = []
state_dir = os.path.join(ROOT_DIR, "state", "versions")
if os.path.exists(state_dir):
    history_dirs = sorted([d for d in os.listdir(state_dir) if os.path.isdir(os.path.join(state_dir, d))], reverse=True)

col6_a, col6_b = st.columns(2)
with col6_a:
    sim_date = st.selectbox("Select Historical Snapshot", history_dirs if history_dirs else ["Current"])
with col6_b:
    sim_strategy = st.selectbox(
        "Simulate Alternative Macro Regime",
        ["default", "defensive_regime", "ai_infrastructure_boom", "liquidity_contraction"]
    )

if st.button("Run Simulation"):
    strat_arg = sim_strategy if sim_strategy != "default" else None
    sim_date_val = sim_date if sim_date != "Current" else "2026_03_13" # Fallback
    result = replay_pipeline(sim_date_val, strat_arg)
    
    if result and "original" in result and "alternative" in result:
        st.markdown("### Simulation Results: Capital Re-allocation")
        comparison_df = pd.DataFrame({
            "Original Allocation": result["original"],
            "Simulated Allocation": result["alternative"]
        })
        st.bar_chart(comparison_df)
    else:
        st.warning("Simulation completed but failed to return chart data. Check system logs.")
