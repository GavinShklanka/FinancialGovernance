import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_market_data

st.set_page_config(page_title="Ecosystems | Lumin Finance", page_icon="◎", layout="wide")
apply_global_styles()

market_data = load_market_data()

page_hero(
    kicker="AI Ecosystem Mapping",
    title="Which assets represent this macro environment?",
    subtitle="Macro signals are mapped to specific industries and companies within the AI infrastructure supply chain. Each asset is scored by its role in the current cycle and its primary structural risk.",
    chips=["Semiconductors", "Hyperscalers", "Infrastructure", "Defense"],
)

if not market_data:
    st.warning("No market data found. Run a pipeline cycle to fetch live data.")
else:
    section_divider("Core Macro Barometers")

    spy = market_data.get("macro", {}).get("SPY", {}).get("price", market_data.get("spy_price", "N/A"))
    vix = market_data.get("macro", {}).get("VIX", {}).get("value", market_data.get("vix", "N/A"))
    gold = market_data.get("macro", {}).get("Gold", {}).get("price", market_data.get("gold_price", "N/A"))
    btc = market_data.get("crypto", {}).get("BTC", {}).get("price", market_data.get("btc_price", "N/A"))

    barometer_cards = []
    if isinstance(spy, (int, float)):
        barometer_cards.append({"eyebrow": "Broad Equity", "title": f"SPY ${spy:,.2f}", "body": "Baseline risk appetite across sectors.", "icon": "📈"})
    if isinstance(vix, (int, float)):
        barometer_cards.append({"eyebrow": "Systemic Volatility", "title": f"VIX {vix:.2f}", "body": "Inverse indicator for growth/infrastructure positioning.", "icon": "📉"})
    if isinstance(gold, (int, float)):
        barometer_cards.append({"eyebrow": "Safe Haven", "title": f"Gold ${gold:,.2f}", "body": "Defends portfolios against liquidity expansion or regime shocks.", "icon": "🥇"})
    if isinstance(btc, (int, float)):
        barometer_cards.append({"eyebrow": "Digital Asset", "title": f"BTC ${btc:,.2f}", "body": "High-beta liquidity sponge and risk-on/off barometer.", "icon": "₿"})

    if barometer_cards:
        card_grid(barometer_cards, columns=4)

    section_divider("AI Ecosystem Watchlist")

    equities = market_data.get("equities", {})
    if not equities:
        st.info("No AI equities retrieved. Run backend fetch cycle.")
    else:
        roles = {
            "NVDA": {"role": "Dominant AI training compute infrastructure", "risk": "High valuation, concentrated capex reliance"},
            "AMD": {"role": "Primary alternative AI compute provider", "risk": "Software moat deficit vs CUDA"},
            "TSM": {"role": "Monopoly fabrication layer for advanced silicon", "risk": "Geopolitical vulnerability"},
            "ASML": {"role": "Monopoly EUV lithography system provider", "risk": "Export restrictions on advanced nodes"},
            "MSFT": {"role": "Hyperscale cloud platform & enterprise AI", "risk": "Capex intensity dragging margins"},
            "AMZN": {"role": "AWS hyperscale cloud & custom silicon", "risk": "Consumer retail cycle exposure"},
            "GOOGL": {"role": "GCP hyperscaler & TPUs", "risk": "Search disruption from LLMs"},
            "META": {"role": "Open source AI models & hyper-engaged network", "risk": "Regulatory headwinds, ad cycle"},
        }

        equity_cards = []
        for ticker, info in roles.items():
            price_data = equities.get(ticker, {}).get("price", "N/A")
            price_str = f"${price_data:,.2f}" if isinstance(price_data, (int, float)) else "N/A"
            equity_cards.append({
                "eyebrow": f"{ticker} · {price_str}",
                "title": info["role"],
                "body": f"Primary Risk: {info['risk']}",
                "footer": f"Live price from backend snapshot",
                "icon": "◈",
            })

        card_grid(equity_cards, columns=4)
