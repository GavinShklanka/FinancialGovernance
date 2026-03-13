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
    st.markdown("### AI Ecosystem Watchlist")
    
    equities = market_data.get("equities", {})
    if not equities:
        st.info("No AI equities retrieved. Run backend fetch cycle.")
    else:
        # Hardcode definitions so the UI can remain completely data-driven on pricing but native on explanations
        roles = {
            "NVDA": {"role": "Dominant AI training compute infrastructure", "risk": "High valuation, concentrated capex reliance"},
            "AMD": {"role": "Primary alternative AI compute provider", "risk": "Software moat deficit vs CUDA"},
            "TSM": {"role": "Monopoly fabrication layer for advanced silicon", "risk": "Geopolitical vulnerability"},
            "ASML": {"role": "Monopoly EUV lithography system provider", "risk": "Export restrictions on advanced nodes"},
            "MSFT": {"role": "Hyperscale cloud platform & enterprise AI", "risk": "Capex intensity dragging margins"},
            "AMZN": {"role": "AWS hyperscale cloud & custom silicon", "risk": "Consumer retail cycle exposure"},
            "GOOGL": {"role": "GCP hyperscaler & TPUs", "risk": "Search disruption from LLMs"},
            "META": {"role": "Open source AI models & hyper-engaged network", "risk": "Regulatory headwinds, ad cycle"}
        }

        col1, col2 = st.columns(2)
        idx = 0
        for ticker, info in roles.items():
            price_data = equities.get(ticker, {}).get("price", "N/A")
            price_str = f"${price_data:,.2f}" if isinstance(price_data, (int, float)) else "N/A"
            
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                st.markdown(f"#### {ticker}")
                st.markdown(f"**Current Price:** <span style='color: #38BDF8; font-weight:bold;'>{price_str}</span>", unsafe_allow_html=True)
                st.markdown(f"**Ecosystem Role:** {info['role']}")
                st.markdown(f"**Primary Risk:** {info['risk']}")
                st.markdown("<br>", unsafe_allow_html=True)
            idx += 1
