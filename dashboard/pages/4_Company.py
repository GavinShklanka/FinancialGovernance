import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_market_data

st.set_page_config(page_title="Company | Lumin Finance", page_icon="◈", layout="wide")
apply_global_styles()

page_hero(
    kicker="Company Intelligence",
    title="Analyst Research Desk",
    subtitle="Select an asset to receive its macro thesis, strategic advantages, and structural risks. All pricing data is fetched from the backend pipeline snapshot.",
    chips=["Thesis", "Advantages", "Risks"],
)

market = load_market_data()

if not market:
    st.warning("No backend market data available. Run the pipeline.")
else:
    available_assets = list(market.get("equities", {}).keys()) + list(market.get("macro", {}).keys()) + list(market.get("crypto", {}).keys())

    if available_assets:
        selected = st.selectbox("Select Asset to Evaluate", available_assets)

        # Find price
        price = "N/A"
        if selected in market.get("equities", {}):
            price = market["equities"][selected].get("price", "N/A")
        elif selected in market.get("macro", {}):
            price = market["macro"][selected].get("price", market["macro"][selected].get("value", "N/A"))
        elif selected in market.get("crypto", {}):
            price = market["crypto"][selected].get("price", "N/A")

        price_str = f"${price:,.2f}" if isinstance(price, (int, float)) else str(price)

        section_divider(f"{selected} Analysis")

        roles = {
            "NVDA": {"thesis": "NVIDIA is the dominant provider of AI training hardware used by hyperscalers.", "pros": ["Dominant AI GPU market share", "Strong pricing power", "Hyperscaler demand expansion"], "cons": ["High valuation", "Geopolitical export risk", "Customer competition (custom silicon)"]},
            "AMD": {"thesis": "AMD serves as the crucial secondary supplier to prevent NVDA monopoly.", "pros": ["Datacenter CPU dominance", "MI300 GPU adoption", "Open ROCm software push"], "cons": ["Lower gross margins", "Still catching up in AI software API"]},
            "TSM": {"thesis": "TSMC is the irreplaceable choke point of global advanced semiconductor manufacturing.", "pros": ["Absolute fabrication monopoly", "Massive pricing power", "Benefiting from all fabless designers"], "cons": ["Taiwan geopolitical risk", "Intensive capital expenditure required"]},
            "ASML": {"thesis": "ASML provides the foundational EUV machines required by TSM to build AI chips.", "pros": ["100% EUV monopoly", "Multi-year backlog", "Irreplaceable technology"], "cons": ["Extreme regulatory export bans", "Slowing trailing-node demand"]},
            "MSFT": {"thesis": "Microsoft integrates OpenAI models directly into global enterprise workflows.", "pros": ["Azure AI growth", "Office 365 Copilot monetization", "Diversified revenue streams"], "cons": ["OpenAI dependency", "Massive required infrastructure capex"]},
            "AMZN": {"thesis": "Amazon Web Services provides the cloud layer and custom silicon.", "pros": ["AWS cloud market leader", "Custom silicon cost advantages", "Strong cash flow"], "cons": ["Retail margin pressure", "Catching up in foundational LLMs"]},
            "GOOGL": {"thesis": "Google holds the deepest internal AI R&D and proprietary TPUs.", "pros": ["TPU infrastructure scale", "DeepMind research lead", "Massive consumer data pool"], "cons": ["Search engine innovator's dilemma", "DOJ anti-trust scrutiny"]},
            "META": {"thesis": "Meta dominates consumer attention and provides the leading open-source models.", "pros": ["Unmatched ad-targeting efficiency", "LLaMA defining open-source standards", "Leaner operating structure"], "cons": ["Reality Labs cash burn", "Regulatory risks"]},
            "SPY": {"thesis": "The S&P 500 represents the broad baseline of American corporate capitalization.", "pros": ["Diversified risk", "Earnings growth baseline"], "cons": ["Concentration in top 7 tech stocks", "Vulnerable to rate hikes"]},
            "VIX": {"thesis": "The Volatility Index prices the implied volatility of S&P 500 options.", "pros": ["Hedge against market crashes", "Mean-reverting asset"], "cons": ["High cost of carry", "Decays in calm markets"]},
            "Gold": {"thesis": "Gold acts as a monetary alternative and defense against systemic debasement.", "pros": ["Zero counterparty risk", "Inflation hedge"], "cons": ["No yield generation", "Opportunity cost vs equities"]},
            "BTC": {"thesis": "Bitcoin operates as a high-beta digital store of value and liquidity sponge.", "pros": ["Absolute scarcity", "Decentralized settlement", "High liquidity sensitivity"], "cons": ["Extreme volatility", "Regulatory uncertainty"]},
            "DXY": {"thesis": "The Dollar Index measures USD strength against a basket of major currencies.", "pros": ["Global reserve currency status", "Flight-to-safety beneficiary"], "cons": ["Headwind for EM and commodities", "Inverse correlation with risk assets"]},
        }

        if selected in roles:
            data = roles[selected]

            analyst_note(
                f"{selected} Macro Thesis — {price_str}",
                data["thesis"],
                tone="accent",
            )

            pros_cards = [{"eyebrow": "Advantage", "title": p, "body": "", "icon": "▲"} for p in data["pros"]]
            cons_cards = [{"eyebrow": "Risk", "title": c, "body": "", "icon": "▼"} for c in data["cons"]]

            section_divider("Strategic Advantages")
            card_grid(pros_cards, columns=3)

            section_divider("Structural Risks")
            card_grid(cons_cards, columns=3)
        else:
            st.info("Detailed analyst briefing unavailable for this specific tracker.")
    else:
        st.warning("No observable assets in the current snapshot.")
