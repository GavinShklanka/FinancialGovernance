import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_signals, load_market_data, load_portfolio_evaluation

st.set_page_config(page_title="Company | Lumin Finance", page_icon="▲", layout="wide")
apply_global_styles()

market = load_market_data()
eval_data = load_portfolio_evaluation()

# ── Asset universe ───────────────────────────────────────────────────────────
_ASSETS = {
    "NVDA": {"name": "NVIDIA", "role": "AI training hardware monopoly", "sector": "Growth"},
    "AMD": {"name": "AMD", "role": "AI inference & custom silicon", "sector": "Growth"},
    "SMH": {"name": "VanEck Semiconductor ETF", "role": "Broad semi exposure", "sector": "Growth"},
    "COPX": {"name": "Global X Copper Miners", "role": "Copper infrastructure play", "sector": "Infrastructure"},
    "URNM": {"name": "Sprott Uranium Miners", "role": "Nuclear AI power thesis", "sector": "Infrastructure"},
    "CIBR": {"name": "First Trust Cybersecurity", "role": "Cybersecurity defense floor", "sector": "Defense"},
    "GLD": {"name": "SPDR Gold Trust", "role": "Safe-haven hedge", "sector": "Defense"},
    "ITA": {"name": "iShares US Aerospace & Defense", "role": "Defense spending cycle", "sector": "Defense"},
}

page_hero(
    kicker="Analyst Research Desk",
    title="What does the evidence say?",
    subtitle="Select an asset to review its thesis, supporting signals, risk factors, and position recommendation.",
    chips=[f"{len(_ASSETS)} Assets Tracked"],
)

# ── Asset selector ───────────────────────────────────────────────────────────
selected = st.selectbox("Select Asset", list(_ASSETS.keys()), format_func=lambda t: f"{t} — {_ASSETS[t]['name']}")
asset_info = _ASSETS[selected]

# Find evaluation decision for this asset
asset_decision = None
if eval_data and eval_data.get("decisions"):
    for d in eval_data["decisions"]:
        if d["ticker"] == selected:
            asset_decision = d
            break

# ── Tabbed Detail View ───────────────────────────────────────────────────────
if asset_decision:
    tab_decision, tab_thesis, tab_risk, tab_execution, tab_history = st.tabs([
        "Decision", "Thesis", "Risk", "Execution", "History"
    ])

    with tab_decision:
        section_divider(f"{selected} — Decision")
        analyst_note(
            f"{asset_decision['action']} · {asset_decision['conviction']} Conviction",
            asset_decision.get("simple_summary", ""),
            tone="success" if asset_decision["action"] in ("BUY_NOW", "SCALE_IN") else (
                "danger" if asset_decision["action"] in ("TRIM", "EXIT") else "warning"
            ),
        )
        card_grid([
            {"eyebrow": "Engine", "title": asset_decision.get("engine", ""), "body": f"Target weight: {asset_decision.get('target_weight_pct', 0):.1%}", "icon": "◈"},
            {"eyebrow": "Regime Alignment", "title": asset_decision.get("regime_alignment", ""), "body": "Current macro regime supports this position.", "icon": "⊕"},
            {"eyebrow": "Timeframe", "title": asset_decision.get("timeframe", ""), "body": f"Entry: {asset_decision.get('entry_strategy', 'N/A')}", "icon": "⏱"},
        ], columns=3)

    with tab_thesis:
        section_divider(f"{selected} — Macro Thesis")
        analyst_note("Investment Thesis", asset_decision.get("thesis", "No thesis available."), tone="accent")
        analyst_note("Strategic Advantage", asset_decision.get("advantage", "No advantage data."), tone="success")

        if asset_decision.get("supporting_signals"):
            section_divider("Supporting Signals")
            signal_cards = [
                {"eyebrow": "SIGNAL", "title": sig, "body": "", "icon": "▲"}
                for sig in asset_decision["supporting_signals"]
            ]
            card_grid(signal_cards, columns=3)

    with tab_risk:
        section_divider(f"{selected} — Risk Assessment")
        analyst_note("Primary Risk", asset_decision.get("primary_risk", "No risk data."), tone="danger")
        analyst_note("Invalidation Trigger", asset_decision.get("invalidation_trigger", "No invalidation criteria."), tone="warning")
        if asset_decision.get("max_drawdown_tolerance"):
            analyst_note("Max Drawdown Tolerance", asset_decision["max_drawdown_tolerance"], tone="warning")

    with tab_execution:
        section_divider(f"{selected} — Execution Plan")
        card_grid([
            {"eyebrow": "Entry Strategy", "title": asset_decision.get("entry_strategy", ""), "body": f"Action: {asset_decision['action']}", "icon": "▶"},
            {"eyebrow": "Exit Conditions", "title": asset_decision.get("exit_conditions", ""), "body": "", "icon": "■"},
            {"eyebrow": "Position Size", "title": f"{asset_decision.get('target_weight_pct', 0):.1%}", "body": asset_decision.get("position_size_rationale", ""), "icon": "◎"},
        ], columns=3)

    with tab_history:
        section_divider(f"{selected} — History")
        analyst_note(
            "Historical Context",
            f"{selected} is positioned within the {asset_decision.get('engine', 'N/A')} engine. "
            f"Regime alignment: {asset_decision.get('regime_alignment', 'N/A')}. "
            f"Signal history tracking will be available as more pipeline runs accumulate.",
            tone="accent",
        )

else:
    # Fallback when no evaluation data exists
    section_divider(f"{selected} — Overview")
    analyst_note(
        f"{asset_info['name']} ({selected})",
        f"Role: {asset_info['role']}. Sector: {asset_info['sector']}. "
        f"Run the pipeline to generate position recommendations.",
        tone="accent",
    )

    # Static advantage/risk cards
    advantage_cards = [
        {"eyebrow": "ROLE", "title": asset_info["role"], "body": f"Tracked within the {asset_info['sector']} engine.", "icon": "▲"},
        {"eyebrow": "SECTOR", "title": asset_info["sector"], "body": "Engine allocation driven by macro regime.", "icon": "◈"},
    ]
    risk_cards = [
        {"eyebrow": "RISK", "title": "General Market Risk", "body": "Macro regime changes can shift allocation away from this position.", "icon": "⚠"},
    ]

    section_divider("Strategic Advantages")
    card_grid(advantage_cards, columns=2)
    section_divider("Structural Risks")
    card_grid(risk_cards, columns=2)
