"""
Antigravity — Streamlit Control Panel (Upgrade 1 & Upgrade 3)

Run with: streamlit run dashboard/antigravity_dashboard.py
"""

import json
import os
import streamlit as st
import pandas as pd
import glob
from sys import path

# Path resolving
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in path:
    path.insert(0, ROOT_DIR)
    
from replay.replay_engine import replay_pipeline

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
REGIME_DIR = os.path.join(ROOT_DIR, "macro_regime")
PORTFOLIO_PATH = os.path.join(ROOT_DIR, "portfolio_model.json")
DECISION_GRAPH_PATH = os.path.join(ROOT_DIR, "decision_graph.json")
ALERTS_PATH = os.path.join(PROCESSED_DIR, "alerts.json")
STATE_DIR = os.path.join(ROOT_DIR, "state", "versions")

def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None

st.set_page_config(page_title="Antigravity Control Panel", layout="wide")

st.title("🛰 Antigravity Control Panel")

# ── Load Data ────────────────────────────────────────────────────────────

signal_data = load_json(os.path.join(PROCESSED_DIR, "signal_snapshot.json"))
regime_data = load_json(os.path.join(REGIME_DIR, "regime_snapshot.json"))
portfolio_data = load_json(PORTFOLIO_PATH)
alerts_data = load_json(ALERTS_PATH)

# We use columns for layout
col_main, col_side = st.columns([2, 1])

with col_main:
    # ── Signal Engine ────────────────────────────────────────────────────────
    st.header("Signal Engine")
    
    if signal_data and "signals" in signal_data:
        st.write(f"**Total Score:** {signal_data.get('total_score', 0):+.2f}")
        
        # Display as a formatted table
        st.markdown("### Active Signals")
        for s in signal_data["signals"]:
            score = float(s["score"])
            if score > 0:
                color = "green"
                arrow = "▲"
            elif score < 0:
                color = "red"
                arrow = "▼"
            else:
                color = "gray"
                arrow = "●"
            
            st.markdown(
                f"<span style='color:{color}'><b>{arrow} {s['name']} ({score:+.1f})</b></span> | {s['explanation']}", 
                unsafe_allow_html=True
            )
    else:
        st.warning("No signal data found.")
        
    st.markdown("---")
    
    # ── Macro Regimes ────────────────────────────────────────────────────────
    st.header("Active Macro Regimes")
    
    if regime_data and "regimes" in regime_data:
        for r in regime_data["regimes"]:
            st.markdown(f"• **{r.replace('_', ' ').title()}**")
            
        st.write("")
        st.markdown("### Rationale")
        for k, v in regime_data.get("regime_rationale", {}).items():
            st.info(f"**{k.replace('_', ' ').title()}**: {v}")
    else:
        st.warning("No regime data found.")

with col_side:
    # ── System Alerts ────────────────────────────────────────────────────────
    st.header("System Alerts")
    
    if alerts_data and "alerts" in alerts_data and alerts_data["alerts"]:
        for alert in alerts_data["alerts"]:
            level = alert.get("level", "WARNING")
            msg = alert.get("message", "")
            
            if level == "CRITICAL":
                st.error(f"CRITICAL: {msg}")
            else:
                st.warning(f"WARNING: {msg}")
    else:
        st.success("No active system alerts.")
        
    st.markdown("---")
    
    # ── Portfolio Engine ─────────────────────────────────────────────────────
    st.header("Portfolio Allocation")
    
    if portfolio_data and "engines" in portfolio_data:
        st.write(f"**Stance:** {portfolio_data.get('stance', 'Unknown').upper()}")
        
        # Build DataFrame for bar chart
        allocations = {}
        for engine in portfolio_data["engines"]:
            allocations[engine["name"]] = engine["allocation_pct"]
            
        allocations["Cash"] = portfolio_data.get("cash_pct", 0)
        
        df = pd.DataFrame({
            "Allocation": list(allocations.values())
        }, index=list(allocations.keys()))
        
        st.bar_chart(df)
        
        with st.expander("View Holdings & Rationale"):
            for engine in portfolio_data["engines"]:
                st.write(f"**{engine['name']}**")
                st.write(f"Holdings: {', '.join(engine['holdings'])}")
                st.write(f"Rationale: {engine['rationale']}")
    else:
        st.warning("No portfolio data found.")

st.markdown("---")

# ── Governance Alerts ──────────────────────────────────────────────────────
st.header("Governance Check")

# We can find governance state from the decision graph
decision_data = load_json(DECISION_GRAPH_PATH)
gov_passed = True
gov_detail = "No governance data found in decision graph."

if decision_data and "nodes" in decision_data:
    for node in decision_data["nodes"]:
        if node["node_type"] == "governance_node":
            if "passed" in node.get("metadata", {}):
                gov_passed = node["metadata"]["passed"]
            gov_detail = node["description"]

if gov_passed:
    st.success(gov_detail)
else:
    st.error(gov_detail)

st.markdown("---")

# ── Historical Replay Mode ──────────────────────────────────────────────────
st.header("Historical Replay Mode")
if os.path.exists(STATE_DIR):
    versions = [d for d in os.listdir(STATE_DIR) if os.path.isdir(os.path.join(STATE_DIR, d))]
    versions.sort(reverse=True)
    
    if versions:
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            selected_date = st.selectbox("Select Historical Week", versions)
        with col_r2:
            alt_strategy = st.selectbox("Alternative Strategy (Optional)", 
                ["", "defensive_regime", "liquidity_contraction", "ai_infrastructure_boom", "commodity_supercycle"])
        
        if st.button("Run Replay / Strategy Comparison"):
            st.info(f"Replaying pipeline for {selected_date}...")
            # We capture stdout or just show it - Streamlit doesn't auto-display print() well,
            # but the user will see it in the console, or we can instruct them to check console.
            # In a full app, replay_engine would return the portfolio models.
            st.markdown(f"**Check terminal for detailed comparison output.**")
            # Convert empty string to None
            strat_val = alt_strategy if alt_strategy else None
            try:
                # Call replay directly 
                replay_pipeline(selected_date, strat_val)
                st.success("Replay calculation completed.")
            except Exception as e:
                st.error(f"Replay failed: {e}")
    else:
        st.info("No historical versions found yet. Run the pipeline to capture state.")
else:
    st.info("No state versioning directory found yet.")
