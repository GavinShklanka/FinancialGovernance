from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape

import streamlit as st


GLOBAL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0F172A;
    --panel: #111827;
    --panel-2: rgba(17, 24, 39, 0.72);
    --panel-3: rgba(15, 23, 42, 0.86);
    --stroke: rgba(148, 163, 184, 0.14);
    --stroke-strong: rgba(56, 189, 248, 0.28);

    --accent: #38BDF8;
    --accent-soft: rgba(56, 189, 248, 0.16);
    --accent-glow: rgba(56, 189, 248, 0.30);

    --success: #22C55E;
    --success-soft: rgba(34, 197, 94, 0.14);

    --warning: #F59E0B;
    --warning-soft: rgba(245, 158, 11, 0.16);

    --danger: #EF4444;
    --danger-soft: rgba(239, 68, 68, 0.14);

    --text-1: #F8FAFC;
    --text-2: #CBD5E1;
    --text-3: #94A3B8;
    --text-4: #64748B;

    --radius-xl: 28px;
    --radius-lg: 22px;
    --radius-md: 18px;
    --radius-sm: 14px;

    --shadow-1: 0 12px 40px rgba(2, 6, 23, 0.28);
    --shadow-2: 0 24px 60px rgba(2, 6, 23, 0.40);
    --shadow-accent: 0 18px 50px rgba(56, 189, 248, 0.18);

    --blur: blur(18px) saturate(140%);
    --transition-fast: 180ms ease;
    --transition-med: 260ms cubic-bezier(.22, 1, .36, 1);
}

html, body, [class*="css"] {
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.12), transparent 28%),
        radial-gradient(circle at 84% 14%, rgba(34, 197, 94, 0.08), transparent 24%),
        radial-gradient(circle at 70% 86%, rgba(245, 158, 11, 0.08), transparent 22%),
        linear-gradient(180deg, #0B1223 0%, #0F172A 42%, #0A1020 100%);
    color: var(--text-1);
}

[data-testid="stHeader"] {
    background: rgba(15, 23, 42, 0.38);
    border-bottom: 1px solid rgba(148, 163, 184, 0.10);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}

[data-testid="stToolbar"] {
    right: 1rem;
    top: 0.6rem;
}

.block-container {
    max-width: 1480px;
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    animation: lumin-fade-up 420ms var(--transition-med);
}

@media (max-width: 1100px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(17, 24, 39, 0.94) 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.10);
    box-shadow: inset -1px 0 0 rgba(255,255,255,0.02);
}

[data-testid="stSidebar"] > div:first-child {
    background:
        radial-gradient(circle at 20% 0%, rgba(56, 189, 248, 0.10), transparent 32%),
        linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(17, 24, 39, 0.98) 100%);
}

[data-testid="stSidebar"] * {
    color: var(--text-2);
}

section[data-testid="stSidebarNav"] {
    padding-top: 0.5rem;
}

section[data-testid="stSidebarNav"] ul {
    gap: 0.35rem;
}

section[data-testid="stSidebarNav"] ul li a {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid transparent;
    border-radius: 16px;
    margin: 0.18rem 0;
    padding: 0.85rem 0.95rem;
    transition:
        transform var(--transition-fast),
        border-color var(--transition-fast),
        box-shadow var(--transition-fast),
        background var(--transition-fast);
}

section[data-testid="stSidebarNav"] ul li a:hover {
    transform: translateX(4px);
    border-color: rgba(56, 189, 248, 0.18);
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.08), rgba(255,255,255,0.02));
    box-shadow: 0 10px 28px rgba(2, 6, 23, 0.24);
    color: var(--text-1);
}

section[data-testid="stSidebarNav"] ul li a[aria-current="page"] {
    color: var(--text-1) !important;
    border-color: rgba(56, 189, 248, 0.34);
    background:
        linear-gradient(90deg, rgba(56, 189, 248, 0.16), rgba(255,255,255,0.03));
    box-shadow:
        0 0 0 1px rgba(56, 189, 248, 0.10),
        0 16px 40px rgba(2, 132, 199, 0.22);
}

/* ---------- TYPOGRAPHY ---------- */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-1) !important;
    letter-spacing: -0.02em;
    font-weight: 700;
}

h1 {
    font-size: clamp(2.3rem, 4vw, 3.8rem) !important;
    line-height: 1.02 !important;
    margin-bottom: 0.35rem !important;
}

h2 {
    font-size: clamp(1.55rem, 2.2vw, 2.2rem) !important;
    margin-top: 0.15rem !important;
    margin-bottom: 0.75rem !important;
}

h3 {
    font-size: clamp(1.15rem, 1.5vw, 1.45rem) !important;
}

p, li, label, .stCaption, div[data-testid="stMarkdownContainer"] p {
    color: var(--text-2);
    line-height: 1.66;
}

small, .lumin-subtle {
    color: var(--text-3) !important;
}

a {
    color: #7DD3FC;
    text-decoration: none;
    transition: color var(--transition-fast);
}
a:hover {
    color: #E0F2FE;
}

/* ---------- DIVIDER ---------- */
hr, [data-testid="stDivider"] {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(56, 189, 248, 0.18) 18%,
        rgba(255,255,255,0.08) 50%,
        rgba(56, 189, 248, 0.18) 82%,
        transparent 100%
    ) !important;
}

/* ---------- METRICS ---------- */
[data-testid="metric-container"],
[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%),
        rgba(17, 24, 39, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 24px;
    box-shadow: var(--shadow-1);
    padding: 1rem 1.1rem !important;
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    transition:
        transform var(--transition-med),
        box-shadow var(--transition-med),
        border-color var(--transition-med);
}

[data-testid="metric-container"]::before,
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    inset: 0 auto auto 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.9;
}

[data-testid="metric-container"]:hover,
[data-testid="stMetric"]:hover {
    transform: translateY(-6px);
    border-color: rgba(56, 189, 248, 0.22);
    box-shadow: var(--shadow-2), var(--shadow-accent);
}

[data-testid="stMetricLabel"] {
    color: var(--text-3) !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.74rem !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-1) !important;
    letter-spacing: -0.03em;
    font-weight: 800 !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button,
[data-testid="baseButton-primary"],
button[kind="primary"] {
    border-radius: 16px !important;
    border: 1px solid rgba(56, 189, 248, 0.22) !important;
    color: #ECFEFF !important;
    font-weight: 700 !important;
    background:
        linear-gradient(180deg, rgba(56, 189, 248, 0.22) 0%, rgba(14, 165, 233, 0.16) 100%) !important;
    box-shadow:
        0 12px 30px rgba(2, 132, 199, 0.18),
        inset 0 1px 0 rgba(255,255,255,0.08);
    transition:
        transform var(--transition-fast),
        box-shadow var(--transition-fast),
        border-color var(--transition-fast),
        filter var(--transition-fast);
}

.stButton > button:hover,
[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover {
    transform: translateY(-2px);
    border-color: rgba(125, 211, 252, 0.35) !important;
    box-shadow:
        0 18px 36px rgba(2, 132, 199, 0.26),
        0 0 0 1px rgba(56, 189, 248, 0.08);
    filter: brightness(1.04);
}

[data-testid="baseButton-secondary"] {
    border-radius: 16px !important;
    border: 1px solid rgba(148, 163, 184, 0.16) !important;
    background: rgba(255,255,255,0.03) !important;
}

/* ---------- INPUTS ---------- */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea,
input {
    border-radius: 16px !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
    background: rgba(15, 23, 42, 0.72) !important;
    border: 1px solid rgba(148, 163, 184, 0.16) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition:
        border-color var(--transition-fast),
        box-shadow var(--transition-fast),
        transform var(--transition-fast) !important;
}

div[data-baseweb="input"] > div:hover,
div[data-baseweb="select"] > div:hover,
textarea:hover {
    border-color: rgba(56, 189, 248, 0.22) !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
textarea:focus {
    border-color: rgba(56, 189, 248, 0.34) !important;
    box-shadow:
        0 0 0 4px rgba(56, 189, 248, 0.14),
        0 12px 26px rgba(2, 6, 23, 0.20) !important;
    transform: translateY(-1px);
}

input, textarea, [data-baseweb="select"] * {
    color: var(--text-1) !important;
}

/* ---------- TABS ---------- */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.55rem;
    margin-bottom: 0.9rem;
}

[data-testid="stTabs"] [role="tab"] {
    height: auto;
    padding: 0.72rem 1rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(148, 163, 184, 0.12);
    color: var(--text-2);
    transition:
        transform var(--transition-fast),
        border-color var(--transition-fast),
        background var(--transition-fast),
        box-shadow var(--transition-fast);
}

[data-testid="stTabs"] [role="tab"]:hover {
    transform: translateY(-1px);
    border-color: rgba(56, 189, 248, 0.24);
    color: var(--text-1);
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--text-1) !important;
    background:
        linear-gradient(180deg, rgba(56, 189, 248, 0.18), rgba(56, 189, 248, 0.10));
    border-color: rgba(56, 189, 248, 0.28);
    box-shadow: 0 10px 28px rgba(2, 132, 199, 0.18);
}

/* ---------- EXPANDERS / ALERTS / CODE ---------- */
[data-testid="stExpander"] details {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)),
        rgba(17, 24, 39, 0.62);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 22px;
    overflow: hidden;
    box-shadow: var(--shadow-1);
}

[data-testid="stExpander"] summary {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
    color: var(--text-1) !important;
    font-weight: 600 !important;
}

[data-testid="stAlert"] {
    border-radius: 18px !important;
    border: 1px solid rgba(148, 163, 184, 0.12) !important;
    background: rgba(17, 24, 39, 0.72) !important;
}

pre, code {
    border-radius: 16px !important;
}

/* ---------- DATAFRAMES / CHARTS ---------- */
[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"],
[data-testid="stVegaLiteChart"],
[data-testid="stPyplotChart"],
[data-testid="stAltairChart"] {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)),
        rgba(17, 24, 39, 0.64);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 24px;
    padding: 0.35rem;
    box-shadow: var(--shadow-1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

/* ---------- CUSTOM HERO / CARD SYSTEM ---------- */
.lumin-hero {
    position: relative;
    overflow: hidden;
    padding: 2rem 2rem 1.6rem 2rem;
    margin: 0 0 1.25rem 0;
    border-radius: 30px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background:
        linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(17, 24, 39, 0.72) 32%, rgba(17, 24, 39, 0.92) 100%);
    box-shadow: var(--shadow-2), inset 0 1px 0 rgba(255,255,255,0.05);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
}

.lumin-hero::before {
    content: "";
    position: absolute;
    inset: auto -18% 20% auto;
    width: 34rem;
    height: 34rem;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.16) 0%, transparent 60%);
    pointer-events: none;
    filter: blur(18px);
}

.lumin-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent 15%, rgba(255,255,255,0.05) 42%, transparent 66%);
    transform: translateX(-120%);
    animation: lumin-sheen 7s ease-in-out infinite;
    pointer-events: none;
}

.lumin-orb {
    position: absolute;
    border-radius: 999px;
    filter: blur(8px);
    opacity: 0.5;
    pointer-events: none;
    animation: lumin-float 8s ease-in-out infinite;
}

.lumin-orb.a {
    top: -32px;
    right: 12%;
    width: 140px;
    height: 140px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.30), transparent 68%);
}

.lumin-orb.b {
    bottom: -46px;
    left: 10%;
    width: 180px;
    height: 180px;
    animation-delay: 1.2s;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.16), transparent 68%);
}

.lumin-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #A5F3FC;
    margin-bottom: 0.7rem;
}

.lumin-kicker::before {
    content: "";
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: var(--accent);
    box-shadow: 0 0 18px var(--accent-glow);
    animation: lumin-pulse 2.2s ease-in-out infinite;
}

.lumin-title {
    margin: 0 0 0.45rem 0;
    color: var(--text-1);
    font-size: clamp(2rem, 3.3vw, 3.4rem);
    line-height: 1.02;
    letter-spacing: -0.04em;
    font-weight: 800;
}

.lumin-subtitle {
    max-width: 72ch;
    margin: 0 0 1rem 0;
    color: var(--text-2);
    font-size: 1rem;
    line-height: 1.72;
}

.lumin-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 0.9rem;
}

.lumin-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.52rem 0.82rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.05);
    color: #E2E8F0;
    border: 1px solid rgba(148, 163, 184, 0.12);
    font-size: 0.84rem;
    font-weight: 600;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.lumin-chip.accent {
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.24);
}
.lumin-chip.success {
    background: rgba(34, 197, 94, 0.12);
    border-color: rgba(34, 197, 94, 0.24);
}
.lumin-chip.warning {
    background: rgba(245, 158, 11, 0.14);
    border-color: rgba(245, 158, 11, 0.26);
}
.lumin-chip.danger {
    background: rgba(239, 68, 68, 0.12);
    border-color: rgba(239, 68, 68, 0.24);
}

.lumin-grid {
    display: grid;
    gap: 1rem;
    margin: 0.8rem 0 1rem 0;
}

.lumin-grid.cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.lumin-grid.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.lumin-grid.cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

@media (max-width: 1100px) {
    .lumin-grid.cols-4,
    .lumin-grid.cols-3,
    .lumin-grid.cols-2 {
        grid-template-columns: 1fr;
    }
}

.lumin-card {
    position: relative;
    overflow: hidden;
    min-height: 100%;
    border-radius: 24px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    background:
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015)),
        rgba(17, 24, 39, 0.66);
    padding: 1.1rem 1.1rem 1rem 1.1rem;
    box-shadow: var(--shadow-1);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    transition:
        transform var(--transition-med),
        box-shadow var(--transition-med),
        border-color var(--transition-med);
}

.lumin-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-2), var(--shadow-accent);
    border-color: rgba(56, 189, 248, 0.22);
}

.lumin-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--accent) 50%, transparent 100%);
    opacity: 0.9;
}

.lumin-card__eyebrow {
    color: #A5F3FC;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-weight: 700;
    font-size: 0.72rem;
    margin-bottom: 0.55rem;
}

.lumin-card__top {
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 0.8rem;
}

.lumin-card__icon {
    flex: 0 0 auto;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 14px;
    display: grid;
    place-items: center;
    background: rgba(56, 189, 248, 0.10);
    border: 1px solid rgba(56, 189, 248, 0.18);
    color: #E0F2FE;
    font-size: 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}

.lumin-card__title {
    color: var(--text-1);
    font-size: 1.03rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.45rem;
}

.lumin-card__body {
    color: var(--text-2);
    font-size: 0.95rem;
    line-height: 1.68;
}

.lumin-card__footer {
    margin-top: 0.9rem;
    color: var(--text-3);
    font-size: 0.82rem;
    font-weight: 600;
}

.lumin-note {
    position: relative;
    overflow: hidden;
    border-radius: 22px;
    padding: 1rem 1.1rem 1rem 1.15rem;
    margin: 0.8rem 0 1rem 0;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)),
        rgba(17, 24, 39, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.12);
    box-shadow: var(--shadow-1);
}

.lumin-note::before {
    content: "";
    position: absolute;
    left: 0;
    top: 12px;
    bottom: 12px;
    width: 4px;
    border-radius: 999px;
    background: var(--accent);
    box-shadow: 0 0 14px var(--accent-glow);
}

.lumin-note.success::before { background: var(--success); box-shadow: 0 0 14px rgba(34, 197, 94, 0.26); }
.lumin-note.warning::before { background: var(--warning); box-shadow: 0 0 14px rgba(245, 158, 11, 0.26); }
.lumin-note.danger::before  { background: var(--danger);  box-shadow: 0 0 14px rgba(239, 68, 68, 0.26); }

.lumin-note__title {
    color: var(--text-1);
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 0.25rem;
}

.lumin-note__body {
    color: var(--text-2);
    line-height: 1.7;
}

.lumin-divider {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1rem 0 1.2rem 0;
    color: var(--text-3);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 700;
}

.lumin-divider::before,
.lumin-divider::after {
    content: "";
    height: 1px;
    flex: 1;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.22), transparent);
}

/* ---------- EXPLANATION TEXT ---------- */
.explanation-text {
    color: var(--text-2) !important;
    font-style: italic;
    font-size: 1.05rem;
}

.metric-value {
    color: var(--accent) !important;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
}

/* ---------- SCROLLBAR ---------- */
*::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
*::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.03);
}
*::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(56, 189, 248, 0.44), rgba(148, 163, 184, 0.22));
    border-radius: 999px;
    border: 2px solid transparent;
    background-clip: padding-box;
}

/* ---------- ANIMATION ---------- */
@keyframes lumin-fade-up {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes lumin-float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50%      { transform: translateY(-10px) scale(1.02); }
}

@keyframes lumin-pulse {
    0%, 100% { transform: scale(1); opacity: 0.95; }
    50%      { transform: scale(1.2); opacity: 1; }
}

@keyframes lumin-sheen {
    0%, 74%, 100% { transform: translateX(-120%); opacity: 0; }
    82%           { opacity: 1; }
    90%           { transform: translateX(120%); opacity: 0.65; }
}

/* ---------- ACCESSIBILITY ---------- */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
    }
}
</style>
"""


# ── Legacy compatibility shim ────────────────────────────────────────────────
def apply_lumin_css() -> None:
    """Legacy name kept for backward compatibility with existing pages."""
    apply_global_styles()


def apply_global_styles(use_st_html: bool = True) -> None:
    """
    Call once near the top of each page, right after st.set_page_config().
    Uses st.html when available, with a safe fallback to st.markdown.
    """
    if use_st_html and hasattr(st, "html"):
        st.html(GLOBAL_STYLE)
    else:
        st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)


def _safe(text: str | None) -> str:
    return escape(text or "").replace("\\n", "<br>")


def page_hero(
    kicker: str,
    title: str,
    subtitle: str,
    chips: Sequence[str] | None = None,
) -> None:
    chips_html = ""
    if chips:
        chips_html = "".join(
            f'<span class="lumin-chip accent">{_safe(chip)}</span>' for chip in chips
        )

    st.markdown(
        f"""
        <section class="lumin-hero">
            <div class="lumin-orb a"></div>
            <div class="lumin-orb b"></div>
            <div class="lumin-kicker">{_safe(kicker)}</div>
            <div class="lumin-title">{_safe(title)}</div>
            <div class="lumin-subtitle">{_safe(subtitle)}</div>
            <div class="lumin-chip-row">{chips_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_divider(label: str) -> None:
    st.markdown(f'<div class="lumin-divider">{_safe(label)}</div>', unsafe_allow_html=True)


def analyst_note(title: str, body: str, tone: str = "accent") -> None:
    tone = tone if tone in {"accent", "success", "warning", "danger"} else "accent"
    st.markdown(
        f"""
        <div class="lumin-note {tone}">
            <div class="lumin-note__title">{_safe(title)}</div>
            <div class="lumin-note__body">{_safe(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_grid(cards: Sequence[Mapping[str, str]], columns: int = 3) -> None:
    col_class = f"cols-{columns if columns in {2, 3, 4} else 3}"
    items = []

    for card in cards:
        eyebrow = _safe(card.get("eyebrow", ""))
        title = _safe(card.get("title", ""))
        body = _safe(card.get("body", ""))
        footer = _safe(card.get("footer", ""))
        icon = _safe(card.get("icon", "✦"))

        items.append(
            f"""
            <article class="lumin-card">
                <div class="lumin-card__top">
                    <div style="flex: 1 1 auto;">
                        {'<div class="lumin-card__eyebrow">' + eyebrow + '</div>' if eyebrow else ''}
                        <div class="lumin-card__title">{title}</div>
                    </div>
                    <div class="lumin-card__icon">{icon}</div>
                </div>
                <div class="lumin-card__body">{body}</div>
                {'<div class="lumin-card__footer">' + footer + '</div>' if footer else ''}
            </article>
            """
        )

    st.markdown(
        f'<section class="lumin-grid {col_class}">{"".join(items)}</section>',
        unsafe_allow_html=True,
    )
