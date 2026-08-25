import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import streamlit as st
from frontend.theme import apply_theme
from frontend.api_client import get_dataset_stats
from datetime import datetime

st.set_page_config(
    page_title="Sentinel AI — Military Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="text-align: center; padding: 40px 0 20px 0;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #E6EDF3; letter-spacing: -1px; margin: 0;">
            🛡️ SENTINEL AI
        </h1>
        <p style="font-size: 1.1rem; color: #58A6FF; margin: 4px 0; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;">
            AI-Powered Military Intelligence Decision Support Platform
        </p>
        <p style="font-size: 0.8rem; color: #8B949E; margin: 0; letter-spacing: 3px;">
            VERSION 2.0 — PRODUCTION RELEASE
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Live System Status ────────────────────────────────────────────────────────
stats = get_dataset_stats()

if stats:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("📂 Total Incidents", f"{stats.get('total_incidents', 0):,}")
    with col2:
        st.metric("💀 Fatalities Recorded", f"{stats.get('total_fatalities', 0):,}")
    with col3:
        st.metric("🤕 Injuries Recorded", f"{stats.get('total_injuries', 0):,}")
    with col4:
        st.metric("🌍 Countries Covered", f"{stats.get('countries_covered', 0):,}")
    with col5:
        st.metric("🗺️ Regions", f"{stats.get('regions_covered', 0)}")
    with col6:
        sources = stats.get('source_datasets', {})
        src_str = " + ".join(sources.keys()) if sources else "Loading..."
        st.metric("📡 Dataset Source", src_str)

    # Date range
    start = stats.get('date_range_start', 'Unknown')
    end = stats.get('date_range_end', 'Unknown')
    updated = stats.get('last_updated', 'Unknown')
    st.markdown(f"""
        <p style="text-align:center; color:#8B949E; font-size:0.8rem; margin-top:8px;">
            Intelligence Coverage: <b style="color:#58A6FF;">{start}</b> to <b style="color:#58A6FF;">{end}</b>
            &nbsp;|&nbsp; Last Updated: <b style="color:#3FB950;">{updated}</b>
        </p>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Backend API not responding. Start with: `uvicorn api.main:app --reload`")

st.markdown("---")

# ── Module Grid ───────────────────────────────────────────────────────────────
st.markdown("### 🗺️ Intelligence Modules")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **📊 Overview**
    Real-time dashboard with global incident statistics, threat heatmap, and dataset metrics from GTD & ACLED.
    """)
    st.markdown("""
    **🎯 Threat Assessment**
    Multi-factor AI risk engine combining ML prediction, historical similarity, regional frequency, and fatality trends. Full explainability.
    """)

with col2:
    st.markdown("""
    **🔍 Incident Explorer**
    Semantic vector search across 200,000+ incidents using FAISS. Filter by country, region, year, attack type, and weapon.
    """)
    st.markdown("""
    **🤖 Intelligence Copilot**
    Conversational AI analyst for strategic briefings, regional summaries, historical comparisons, and executive reports.
    """)

with col3:
    st.markdown("""
    **📈 Analytics**
    Deep analytics from real GTD + ACLED data: global heatmaps, country rankings, fatality trends, attack distributions, and regional comparisons.
    """)
    st.markdown("""
    **🗺️ Intelligence Map**
    Interactive clustered world map with threat-colored markers, popup intelligence summaries, and geographic heatmap overlay.
    """)

st.markdown("---")

# ── System Status ─────────────────────────────────────────────────────────────
st.markdown("### ⚙️ System Status")

col1, col2, col3, col4 = st.columns(4)
with col1:
    api_status = "🟢 ONLINE" if stats else "🔴 OFFLINE"
    st.markdown(f"**API Backend:** {api_status}")
with col2:
    st.markdown("**Risk Engine:** 🟢 ML + Heuristic")
with col3:
    st.markdown("**RAG / FAISS:** 🟢 Vector Search")
with col4:
    st.markdown("**Live Intel:** 🟡 Historical Mode")

st.markdown(f"""
    <p style="text-align:center; color:#30363D; font-size:0.7rem; margin-top: 40px;">
        Sentinel AI Version 2.0 — Internal Intelligence Use Only — {datetime.utcnow().strftime('%Y')}
    </p>
""", unsafe_allow_html=True)
