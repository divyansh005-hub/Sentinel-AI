import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import streamlit as st
import plotly.express as px
from frontend.theme import apply_theme
from frontend.components.widgets import render_metric_card, render_status_bar
from frontend.api_client import get_dataset_stats, get_analytics

st.set_page_config(page_title="Overview Dashboard", page_icon="📊", layout="wide")
apply_theme()
render_status_bar()

st.title("📊 Global Incident Dashboard")
st.markdown("Real-time telemetry and intelligence metrics based on integrated GTD & ACLED datasets.")

stats = get_dataset_stats()

if stats:
    # ── Key Metrics ───────────────────────────────────────────────────────────
    st.markdown("### 📈 Core Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Incidents", f"{stats['total_incidents']:,}", icon="📂", color="#58A6FF")
    with c2:
        render_metric_card("Total Fatalities", f"{stats['total_fatalities']:,}", icon="💀", color="#F85149")
    with c3:
        render_metric_card("Active Regions", f"{stats['regions_covered']:,}", icon="🌍", color="#D2991F")
    with c4:
        render_metric_card("Countries Affected", f"{stats['countries_covered']:,}", icon="🗺️", color="#3FB950")

    st.markdown("---")

    # ── Analytics Row 1 ───────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📅 Temporal Threat Evolution (Incidents)")
        timeline_data = get_analytics("incident_timeline")
        if timeline_data:
            fig = px.area(
                x=timeline_data['labels'], 
                y=timeline_data['values'], 
                template="plotly_dark",
                color_discrete_sequence=['#58A6FF']
            )
            fig.update_layout(
                paper_bgcolor="#0D1117", 
                plot_bgcolor="#0D1117",
                xaxis_title="Month", 
                yaxis_title="Incident Count",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            fig.update_traces(fillcolor='rgba(88, 166, 255, 0.2)', line=dict(width=2))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.markdown("### 📡 Top Threat Areas")
        if stats.get('high_threat_areas'):
            for country, count in stats['high_threat_areas'].items():
                st.markdown(f"""
                <div style="background:#161B22; border:1px solid #21262D; border-left:3px solid #F85149; padding:10px 15px; margin-bottom:10px; border-radius:4px; display:flex; justify-content:space-between;">
                    <span style="font-weight:600; color:#E6EDF3;">{country}</span>
                    <span style="color:#8B949E;">{count:,} incidents</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No high threat areas identified.")

    st.markdown("---")
    
    # ── Analytics Row 2 ───────────────────────────────────────────────────────
    c3, c4, c5 = st.columns(3)
    
    with c3:
        st.markdown("### ⚔️ Attack Distribution")
        if stats.get('top_attack_types'):
            labels = list(stats['top_attack_types'].keys())
            values = list(stats['top_attack_types'].values())
            fig_pie = px.pie(
                names=labels, 
                values=values, 
                hole=0.4, 
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.YlOrRd[::-1]
            )
            fig_pie.update_layout(
                paper_bgcolor="#0D1117",
                plot_bgcolor="#0D1117",
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with c4:
        st.markdown("### 🌍 Top Countries by Incident")
        if stats.get('top_countries'):
            labels = list(stats['top_countries'].keys())[:7]
            values = list(stats['top_countries'].values())[:7]
            fig_bar = px.bar(
                x=values,
                y=labels,
                orientation='h',
                template="plotly_dark",
                color=values,
                color_continuous_scale="Reds"
            )
            fig_bar.update_layout(
                paper_bgcolor="#0D1117",
                plot_bgcolor="#0D1117",
                xaxis_title="Incidents",
                yaxis_title="",
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis={'categoryorder':'total ascending'},
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with c5:
        st.markdown("### 📚 Dataset Composition")
        if stats.get('source_datasets'):
            labels = list(stats['source_datasets'].keys())
            values = list(stats['source_datasets'].values())
            fig_ds = px.pie(
                names=labels, 
                values=values,
                hole=0.6,
                template="plotly_dark",
                color_discrete_sequence=['#58A6FF', '#3FB950', '#D2991F']
            )
            fig_ds.update_layout(
                paper_bgcolor="#0D1117",
                plot_bgcolor="#0D1117",
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            fig_ds.update_traces(textinfo='value')
            st.plotly_chart(fig_ds, use_container_width=True)

else:
    st.error("❌ Failed to connect to the intelligence backend or database is empty.")
    st.info("Run `python setup_data_pipeline.py` to ingest GTD and ACLED data, then ensure the backend is running.")
