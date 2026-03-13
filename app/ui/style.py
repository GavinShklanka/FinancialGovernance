import streamlit as st

def apply_lumin_css():
    st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
        color: white;
    }
    .css-1d391kg {
        background-color: transparent !important;
    }
    div[data-testid="stVerticalBlock"] > div > div {
        background: rgba(17, 24, 39, 0.9); /* #111827 panel color */
        border-radius: 12px;
        padding: 5px;
    }
    h1, h2, h3, h4 {
        color: #38BDF8 !important; /* accent */
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #38BDF8; /* accent */
    }
    .success-text { color: #22C55E; font-weight: bold; } /* success */
    .warning-text { color: #F59E0B; font-weight: bold; } /* warning */
    .danger-text { color: #EF4444; font-weight: bold; } /* danger */
    .explanation-text {
        font-size: 14px;
        color: #94A3B8;
        font-style: italic;
    }
    /* Simple divider override */
    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)
