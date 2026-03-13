import streamlit as st
import os, sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.ui.style import apply_lumin_css

st.set_page_config(page_title="Ecosystems | Lumin Finance", layout="wide")
apply_lumin_css()

st.header("Which companies benefit from this macro environment?")
st.markdown("<p class='explanation-text'>AI Ecosystem Intelligence</p>", unsafe_allow_html=True)
st.divider()

ecosystems = {
    "AI Infrastructure": [
        {"name": "NVIDIA", "position": "GPU Monopoly", "exposure": "High", "growth": "120% YoY", "moat": "CUDA Software Stack"},
        {"name": "TSMC", "position": "Foundry Monopoly", "exposure": "High", "growth": "25% YoY", "moat": "Advanced Packaging"},
        {"name": "ASML", "position": "EUV Monopoly", "exposure": "High", "growth": "15% YoY", "moat": "Lithography Patents"}
    ],
    "Cyber Defense": [
        {"name": "Palo Alto", "position": "Enterprise Sec", "exposure": "Med", "growth": "20% YoY", "moat": "Platform Consolidation"},
        {"name": "CrowdStrike", "position": "Endpoint Sec", "exposure": "High", "growth": "35% YoY", "moat": "AI Threat Graph"}
    ]
}

for eco, companies in ecosystems.items():
    st.markdown(f"### {eco}")
    cols = st.columns(len(companies))
    for idx, comp in enumerate(companies):
        with cols[idx % len(cols)]:
            st.markdown(f"#### {comp['name']}")
            st.markdown(f"**Market Position:** {comp['position']}")
            st.markdown(f"**AI Exposure:** {comp['exposure']}")
            st.markdown(f"**Revenue Growth:** {comp['growth']}")
            st.markdown(f"**Industry Moat:** {comp['moat']}")
    st.divider()
