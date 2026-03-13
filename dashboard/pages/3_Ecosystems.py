import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css

st.set_page_config(page_title="Ecosystems | Lumin Finance", layout="wide")
apply_lumin_css()

from app.ui.data_bridge import load_market_data

st.header("Which assets represent this macro environment?")
st.markdown("<p class='explanation-text'>Authentic AI Ecosystem Data Mapping</p>", unsafe_allow_html=True)
st.divider()

market_data = load_market_data()

if not market_data:
    st.warning("No market data found in the backend JSON cache. Run a pipeline cycle to fetch live data constraints.")
else:
    # We only have raw indices right now via market_snapshot, so we map the available intelligence
    # rather than hallucinating fundamental metrics.
    
    st.markdown("### Core Macro Barometers")
    colA, colB, colC = st.columns(3)
    
    spy = market_data.get("equities", {}).get("SPY", {}).get("price", "N/A")
    vix = market_data.get("macro", {}).get("VIX", {}).get("value", "N/A")
    gold = market_data.get("macro", {}).get("Gold", {}).get("price", "N/A")
    btc = market_data.get("crypto", {}).get("BTC", {}).get("price", "N/A")
    
    with colA:
        st.markdown("#### Broad Equity (SPY)")
        if isinstance(spy, (int, float)):
             st.markdown(f"<div class='metric-value'>${spy:,.2f}</div>", unsafe_allow_html=True)
        else:
             st.markdown(f"<div class='metric-value'>No Price</div>", unsafe_allow_html=True)
        st.markdown("Role: Baseline risk appetite across sectors.")
        
    with colB:
        st.markdown("#### Systemic Volatility (VIX)")
        if isinstance(vix, (int, float)):
             st.markdown(f"<div class='metric-value'>{vix:.2f}</div>", unsafe_allow_html=True)
        else:
             st.markdown(f"<div class='metric-value'>No Value</div>", unsafe_allow_html=True)
        st.markdown("Role: Inverse indicator for growth/infrastructure positioning.")
        
    with colC:
        st.markdown("#### Safe Haven / Alternatives")
        st.markdown(f"**Gold:** ${gold:,.2f}" if isinstance(gold, (int, float)) else "**Gold:** N/A")
        st.markdown(f"**Bitcoin:** ${btc:,.2f}" if isinstance(btc, (int, float)) else "**Bitcoin:** N/A")
        st.markdown("Role: Defends portfolios against liquidity expansion or regime shocks.")

    st.divider()
    st.markdown("### Specific AI Company Metrics")
    st.info("The fundamental backend processor is currently restricted to broad macro scopes. Company-level intelligence (growth Moats, specific revenues) requires an expansion of the Antigravity Alpha Vantage connector to stock-specific tickers.")
