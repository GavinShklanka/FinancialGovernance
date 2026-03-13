import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css

st.set_page_config(page_title="Company Research | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("Company Intelligence")
st.markdown("<p class='explanation-text'>Evaluating specific assets in this macro context.</p>", unsafe_allow_html=True)
st.divider()

from app.ui.data_bridge import load_market_data

st.header("Company Intelligence")
st.markdown("<p class='explanation-text'>Evaluating specific assets in this macro context.</p>", unsafe_allow_html=True)
st.divider()

market = load_market_data()

if not market:
    st.warning("No backend market data available. Run the pipeline.")
else:
    # We only have a few top-level assets right now in the backend
    available_assets = list(market.get("equities", {}).keys()) + list(market.get("macro", {}).keys()) + list(market.get("crypto", {}).keys())
    
    if available_assets:
        selected = st.selectbox("Select Asset to Evaluate (Powered by live snapshot)", available_assets)
        
        st.markdown(f"### {selected} Snapshot")
        
        # Try to find the price
        price = "N/A"
        if selected in market.get("equities", {}): price = market["equities"][selected].get("price", "N/A")
        elif selected in market.get("macro", {}): price = market["macro"][selected].get("price", market["macro"][selected].get("value", "N/A"))
        elif selected in market.get("crypto", {}): price = market["crypto"][selected].get("price", "N/A")
        
        st.markdown(f"**Current Valuation / Index:** {price}")
        st.markdown("---")
        st.info(f"The `company_research` engine is currently disabled in the backend architecture. To view dynamic P/E ratios, Revenue YoY bounds, and fundamental Cons/Risks for `{selected}`, the Antigravity fundamental scraper must be integrated.")
    else:
        st.warning("No observable assets in the current snapshot.")
