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

st.selectbox("Select Asset to Evaluate", ["NVIDIA (NVDA)", "TSMC (TSM)", "ASML (ASML)"])

st.markdown("### NVIDIA Investment Thesis")
st.markdown("Dominant AI compute provider with strong pricing power and growing demand from hyperscaler AI infrastructure investment.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Pros")
    st.markdown("""
    • 80%+ AI GPU market share  
    • Hyperscaler capex expansion  
    • High gross margins  
    • AI training demand rising  
    """)

with col2:
    st.markdown("#### Cons / Risks")
    st.markdown("""
    • High valuation  
    • China export restrictions  
    • Competition from custom silicon  
    """)
