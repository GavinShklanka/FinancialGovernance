import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css
from app.ui.data_bridge import load_alerts

st.set_page_config(page_title="Risk Monitor | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("What could break this thesis?")
st.markdown("<p class='explanation-text'>Risk Monitoring Panel</p>", unsafe_allow_html=True)
st.divider()

alerts = load_alerts().get("alerts", [])

if not alerts:
    st.markdown("<p class='success-text'>No severe macro risks currently detected by the Alert Engine.</p>", unsafe_allow_html=True)
else:
    for alert in alerts:
        severity = alert.get("severity", "info")
        msg = alert.get("message", "")
        if severity == "high":
            st.error(f"⚠ CRITICAL RISK: {msg}")
            st.markdown(f"<p class='explanation-text'>Historical backtesting indicates this significantly pressures current infrastructure valuations by altering the risk-free rate or tightening available liquidity.</p>", unsafe_allow_html=True)
        elif severity == "medium":
            st.warning(f"⚠ ELEVATED RISK: {msg}")
            st.markdown(f"<p class='explanation-text'>Monitored signal variation could transition the environment away from the optimal positioning thesis.</p>", unsafe_allow_html=True)
        else:
            st.info(f"NOTICE: {msg}")

st.divider()
st.header("Governance & Compliance")
st.markdown("<p class='explanation-text'>Checking algorithmic allocations against active risk boundaries.</p>", unsafe_allow_html=True)

from app.ui.data_bridge import load_governance
gov = load_governance()

if gov.get("status") == "passed":
    st.success("✓ GOVERNANCE CHECKS PASSED: Portfolio engine complies with all defined risk and position limits.")
else:
    st.error("⚠ GOVERNANCE CHECKS FAILED: Strategy allocation violates constraints.")
    for violation in gov.get("violations", []):
        st.markdown(f"**[{violation.get('severity', 'HIGH')}] {violation.get('rule', 'Unknown Rule')}**")
        st.markdown(f"*{violation.get('detail', '')}*")
