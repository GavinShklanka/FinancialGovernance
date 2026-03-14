import streamlit as st
import os, sys, json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_global_styles, page_hero, section_divider, analyst_note, card_grid
from app.ui.data_bridge import load_portfolio, load_portfolio_evaluation

st.set_page_config(page_title="Portfolio | Lumin Finance", page_icon="▲", layout="wide")
apply_global_styles()

portfolio_data = load_portfolio()
eval_data = load_portfolio_evaluation()

engines = portfolio_data.get("engines", [])
cash_pct = portfolio_data.get("cash_pct", 0)
stance = portfolio_data.get("stance", "neutral")

# ── Hero ─────────────────────────────────────────────────────────────────────
page_hero(
    kicker="Capital Strategy",
    title="Where should capital go?",
    subtitle="The portfolio engine uses three strategy engines — Growth, Infrastructure, and Defense — based on the active macro regime and signal evidence.",
    chips=[f"Stance: {stance.upper()}", f"Cash: {cash_pct:.0%}"],
)

# ── Mode Switch ──────────────────────────────────────────────────────────────
view_mode = st.radio(
    "View Mode",
    ["Simple", "Analyst", "Execution"],
    horizontal=True,
    label_visibility="collapsed",
)

# ── Floating Decision Cards ──────────────────────────────────────────────────
if eval_data and eval_data.get("decisions"):
    section_divider("Portfolio Decisions")

    decisions = eval_data["decisions"]

    # Group by action
    buy_now = [d for d in decisions if d["action"] == "BUY_NOW"]
    scale_in = [d for d in decisions if d["action"] == "SCALE_IN"]
    hold = [d for d in decisions if d["action"] == "HOLD"]
    trim = [d for d in decisions if d["action"] in ("TRIM", "EXIT")]

    action_groups = [
        ("🟢 Buy Now", buy_now, "success"),
        ("🔵 Scale In", scale_in, "accent"),
        ("⚪ Hold", hold, "warning"),
        ("🔴 Trim", trim, "danger"),
    ]

    for label, group, tone in action_groups:
        if not group:
            continue

        summary_cards = []
        for d in group:
            if view_mode == "Simple":
                body = d.get("simple_summary", "")
            elif view_mode == "Analyst":
                body = d.get("analyst_summary", "")
            else:
                body = (
                    f"Entry: {d.get('entry_strategy', 'N/A')} | "
                    f"Target: {d.get('target_weight_pct', 0):.1%} | "
                    f"Timeframe: {d.get('timeframe', 'N/A')}"
                )

            summary_cards.append({
                "eyebrow": f"{d['action']} · {d['conviction']}",
                "title": d["ticker"],
                "body": body,
                "icon": "▲" if d["action"] in ("BUY_NOW", "SCALE_IN") else ("●" if d["action"] == "HOLD" else "▼"),
            })

        analyst_note(label, f"{len(group)} position(s)", tone=tone)
        card_grid(summary_cards, columns=min(len(summary_cards), 4))

    # ── Expandable Detail Panels ─────────────────────────────────────────────
    section_divider("Asset Details")

    for d in decisions:
        with st.expander(f"**{d['ticker']}** — {d['action']} ({d['conviction']})"):
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.markdown(f"**Engine:** {d.get('engine', 'N/A')}")
                st.markdown(f"**Target Weight:** {d.get('target_weight_pct', 0):.1%}")
                st.markdown(f"**Timeframe:** {d.get('timeframe', 'N/A')}")
                st.markdown(f"**Entry:** {d.get('entry_strategy', 'N/A')}")
            with dcol2:
                st.markdown(f"**Thesis:** {d.get('thesis', 'N/A')}")
                st.markdown(f"**Risk:** {d.get('primary_risk', 'N/A')}")
                st.markdown(f"**Invalidation:** {d.get('invalidation_trigger', 'N/A')}")
                st.markdown(f"**Exit:** {d.get('exit_conditions', 'N/A')}")

            if d.get("supporting_signals"):
                st.markdown("**Supporting Signals:** " + " · ".join(d["supporting_signals"]))


# ── Engine Allocation Cards ──────────────────────────────────────────────────
section_divider("Engine Allocations")

engine_cards = []
for engine in engines:
    engine_cards.append({
        "eyebrow": f"{engine['allocation_pct']:.0%} Allocation",
        "title": engine["name"],
        "body": engine.get("rationale", "No rationale provided."),
        "icon": "◈" if "Growth" in engine["name"] else ("◇" if "Infrastructure" in engine["name"] else "▲"),
    })
engine_cards.append({
    "eyebrow": f"{cash_pct:.0%} Reserve",
    "title": "Cash",
    "body": "Cash reserve for rebalancing, opportunistic entries, and risk reduction.",
    "icon": "●",
})
card_grid(engine_cards, columns=4)

# ── Strategy Rationale ───────────────────────────────────────────────────────
overall_rationale = portfolio_data.get("overall_rationale", "")
if overall_rationale:
    analyst_note("Strategy Rationale", overall_rationale, tone="accent")

# ── Plotly Donut ─────────────────────────────────────────────────────────────
try:
    import plotly.graph_objects as go

    labels = [e["name"] for e in engines] + ["Cash"]
    values = [e["allocation_pct"] for e in engines] + [cash_pct]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=["#38BDF8", "#22C55E", "#F59E0B", "#94A3B8"]),
        textinfo="label+percent",
        textposition="inside",
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#CBD5E1",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)
except ImportError:
    st.info("Install plotly for the allocation donut chart.")

# ── Download Reports ─────────────────────────────────────────────────────────
section_divider("Export Reports")

dl1, dl2 = st.columns(2)

json_path = os.path.join(ROOT_DIR, "data", "processed", "reports", "latest_portfolio_evaluation.json")
md_path = os.path.join(ROOT_DIR, "data", "processed", "reports", "latest_portfolio_evaluation.md")

with dl1:
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            st.download_button(
                "⬇ Download JSON Report",
                f.read(),
                file_name="portfolio_evaluation.json",
                mime="application/json",
            )
    else:
        st.info("Run the pipeline to generate the JSON report.")

with dl2:
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            st.download_button(
                "⬇ Download Markdown Report",
                f.read(),
                file_name="portfolio_evaluation.md",
                mime="text/markdown",
            )
    else:
        st.info("Run the pipeline to generate the Markdown report.")
