import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_portfolio

st.set_page_config(page_title="Portfolio | Lumin Finance", page_icon="▲", layout="wide")
apply_global_styles()

portfolio = load_portfolio()
engines = portfolio.get("engines", [])
stance = portfolio.get("stance", "neutral").upper()
cash_pct = portfolio.get("cash_pct", 0)
overall_rationale = portfolio.get("overall_rationale", "No overall rationale provided.")

page_hero(
    kicker="Capital Strategy",
    title="Where should capital go?",
    subtitle="The portfolio engine allocates capital across three strategy engines — Growth, Infrastructure, and Defense — based on the current macro regime and signal evidence.",
    chips=[f"Stance: {stance}", f"Cash: {cash_pct * 100:.0f}%"],
)

analyst_note("Overall Strategy Rationale", overall_rationale, tone="accent")

section_divider("Engine Allocations")

if engines:
    engine_cards = []
    for eng in engines:
        pct = eng.get("allocation_pct", 0)
        engine_cards.append({
            "eyebrow": f"{pct * 100:.0f}% Allocation",
            "title": eng.get("name", "Unknown Engine"),
            "body": eng.get("rationale", "No rationale provided by model."),
            "footer": f"Driven by aggregate signal score",
            "icon": "◈" if "Growth" in eng.get("name", "") else "◎" if "Infrastructure" in eng.get("name", "") else "▲",
        })
    card_grid(engine_cards, columns=len(engine_cards) if len(engine_cards) <= 4 else 3)

    # Allocation visualization
    section_divider("Allocation Breakdown")

    import plotly.express as px
    import pandas as pd

    labels = [e.get("name", "?") for e in engines]
    values = [e.get("allocation_pct", 0) for e in engines]
    if cash_pct > 0:
        labels.append("Cash")
        values.append(cash_pct)

    df = pd.DataFrame({"Engine": labels, "Weight": values})
    fig = px.pie(
        df,
        names="Engine",
        values="Weight",
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F59E0B", "#EF4444"],
        hole=0.45,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#CBD5E1",
        legend=dict(font=dict(color="#CBD5E1")),
        margin=dict(t=20, b=20, l=20, r=20),
    )
    fig.update_traces(textfont_color="#F8FAFC")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No engine data available. Run the pipeline.")
