import streamlit as st
import os
import sys

# Ensure root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css

st.set_page_config(
    page_title="Lumin Finance",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_lumin_css()

st.title("Lumin Finance")
st.markdown("*AI Supercycle Intelligence Terminal*")
st.divider()

st.markdown("""
### Welcome to Lumin Finance
This is an institutional-grade financial intelligence software. 

Please use the **Sidebar** to navigate through the investor narrative:

1. **Discover**: What is happening in the world right now?
2. **Signals**: What evidence is driving this conclusion?
3. **Ecosystems**: Which companies benefit?
4. **Company**: How do we evaluate these assets?
5. **Portfolio**: Where should capital go?
6. **Monitor**: What could break this thesis?
7. **Forecast**: What might happen next?
""")
