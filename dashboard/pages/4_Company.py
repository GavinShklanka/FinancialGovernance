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
        
        # Pull definition mapping
        roles = {
            "NVDA": {"thesis": "NVIDIA is the dominant provider of AI training hardware used by hyperscalers.", "pros": ["Dominant AI GPU market share", "Strong pricing power", "Hyperscaler demand expansion"], "cons": ["High valuation", "Geopolitical export risk", "Customer competition (custom silicon)"]},
            "AMD": {"thesis": "AMD serves as the crucial secondary supplier to prevent NVDA monopoly.", "pros": ["Datacenter CPU dominance", "MI300 GPU adoption", "Open ROCm software push"], "cons": ["Lower gross margins", "Still catching up in AI software API"]},
            "TSM": {"thesis": "TSMC is the irreplaceable choke point of global advanced semiconductor manufacturing.", "pros": ["Absolute fabrication monopoly", "Massive pricing power", "Benefiting from all fabless designers"], "cons": ["Taiwan geopolitical risk", "Intensive capital expenditure required"]},
            "ASML": {"thesis": "ASML provides the foundational EUV machines required by TSM to build AI chips.", "pros": ["100% EUV monopoly", "Multi-year backlog", "Irreplaceable technology"], "cons": ["Extreme regulatory export bans", "Slowing trailing-node demand"]},
            "MSFT": {"thesis": "Microsoft integrates OpenAI models directly into global enterprise workflows.", "pros": ["Azure AI growth", "Office 365 Copilot monetization", "Diversified revenue streams"], "cons": ["OpenAI dependency", "Massive required infrastructure capex"]},
            "AMZN": {"thesis": "Amazon Web Services provides the cloud layer and custom silicon (Inferentia/Trainium).", "pros": ["AWS cloud market leader", "Custom silicon cost advantages", "Strong cash flow"], "cons": ["Retail margin pressure", "Catching up in foundational LLMs"]},
            "GOOGL": {"thesis": "Google holds the deepest internal AI R&D and proprietary TPUs.", "pros": ["TPU infrastructure scale", "DeepMind research lead", "Massive consumer data pool"], "cons": ["Search engine innovator's dilemma", "DOJ anti-trust scrutiny"]},
            "META": {"thesis": "Meta dominates consumer attention and provides the leading open-source models (LLaMA).", "pros": ["Unmatched ad-targeting efficiency", "LLaMA defining open-source standards", "Leaner operating structure"], "cons": ["Reality Labs cash burn", "Regulatory risks"]},
            "SPY": {"thesis": "The S&P 500 represents the broad baseline of American corporate capitalization.", "pros": ["Diversified risk", "Earnings growth baseline"], "cons": ["Concentration in top 7 tech stocks", "Vulnerable to rate hikes"]},
            "VIX": {"thesis": "The Volatility Index prices the implied volatility of S&P 500 options.", "pros": ["Hedge against market crashes", "Mean-reverting asset"], "cons": ["High cost of carry", "Decays in calm markets"]},
            "Gold": {"thesis": "Gold acts as a monetary alternatives and defense against systemic debasement.", "pros": ["Zero counterparty risk", "Inflation hedge"], "cons": ["No yield generation", "Opportunity cost vs equities"]},
            "BTC": {"thesis": "Bitcoin operates as a high-beta digital store of value and liquidity sponge.", "pros": ["Absolute scarcity", "Decentralized settlement", "High liquidity sensitivity"], "cons": ["Extreme volatility", "Regulatory uncertainty"]}
        }

        if selected in roles:
            data = roles[selected]
            st.markdown(f"#### {selected} Macro Thesis")
            st.markdown(f"<div style='font-size:18px; margin-bottom: 20px;'>{data['thesis']}</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Strategic Advantages")
                for p in data['pros']:
                    st.markdown(f"• {p}")
            with c2:
                st.markdown("#### Structural Risks")
                for c in data['cons']:
                    st.markdown(f"• {c}")
        else:
             st.info("Detailed analyst briefing unavailable for this specific tracker.")
    else:
        st.warning("No observable assets in the current snapshot.")
