import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from frontend.theme import apply_theme
from frontend.components.widgets import render_status_bar
from frontend.api_client import get_analytics

st.set_page_config(page_title="Deep Analytics", page_icon="📈", layout="wide")
apply_theme()
render_status_bar()

st.title("📈 Advanced Analytics")
st.markdown("Deep dive into historical trends, feature correlations, and system performance from the unified intelligence database.")

# ── Filters ─────────────────────────────────────────────────────────────────
with st.expander("⚙️ Analytics Filters", expanded=False):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        country_filter = st.text_input("Filter by Country")
    with f_col2:
        region_filter = st.text_input("Filter by Region")
    with f_col3:
        c_yr1, c_yr2 = st.columns(2)
        year_from = c_yr1.number_input("Year From", min_value=1970, max_value=2026, value=None, step=1)
        year_to = c_yr2.number_input("Year To", min_value=1970, max_value=2026, value=None, step=1)

def get_filtered_analytics(chart_type: str, top_n: int = 10):
    return get_analytics(
        chart_type=chart_type,
        country=country_filter if country_filter else None,
        region=region_filter if region_filter else None,
        year_from=year_from if year_from else None,
        year_to=year_to if year_to else None,
        top_n=top_n
    )

st.markdown("---")

# ── Row 1: Regional & Target Comparisons ─────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Regional Impact Comparison")
    reg_data = get_filtered_analytics("regional_comparison", top_n=8)
    if reg_data and 'regions' in reg_data:
        fig1 = go.Figure(data=[
            go.Bar(name='Incidents', x=reg_data['regions'], y=reg_data['incidents'], marker_color='#58A6FF'),
            go.Bar(name='Fatalities', x=reg_data['regions'], y=reg_data['fatalities'], marker_color='#F85149')
        ])
        fig1.update_layout(
            barmode='group', template="plotly_dark",
            paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Insufficient data for regional comparison.")

with c2:
    st.subheader("Primary Target Types")
    tgt_data = get_filtered_analytics("target_distribution", top_n=10)
    if tgt_data and 'labels' in tgt_data:
        fig2 = px.bar(
            x=tgt_data['values'], y=tgt_data['labels'], orientation='h',
            template="plotly_dark", color=tgt_data['values'], color_continuous_scale="Blues"
        )
        fig2.update_layout(
            paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
            xaxis_title="Incidents", yaxis_title="",
            yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Insufficient data for target distribution.")

st.markdown("---")

# ── Row 2: Yearly Fatality Trends & Weapons ──────────────────────────────────
c3, c4 = st.columns([2, 1])

with c3:
    st.subheader("Global Fatality Trend")
    fat_data = get_filtered_analytics("fatality_trend")
    if fat_data and 'labels' in fat_data:
        fig3 = px.line(
            x=fat_data['labels'], y=fat_data['values'], markers=True,
            template="plotly_dark", color_discrete_sequence=['#F85149']
        )
        fig3.update_layout(
            paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
            xaxis_title="Year", yaxis_title="Total Fatalities"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Insufficient data for fatality trend.")

with c4:
    st.subheader("Weapon Utilization")
    weap_data = get_filtered_analytics("weapon_distribution", top_n=5)
    if weap_data and 'labels' in weap_data:
        fig4 = px.pie(
            names=weap_data['labels'], values=weap_data['values'], hole=0.5,
            template="plotly_dark", color_discrete_sequence=px.colors.sequential.OrRd[::-1]
        )
        fig4.update_layout(
            paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Insufficient data for weapon distribution.")

st.markdown("---")

# ── Row 3: Monthly Seasonality ───────────────────────────────────────────────
st.subheader("Monthly Incident Seasonality")
mo_data = get_filtered_analytics("monthly_trend")
if mo_data and 'labels' in mo_data:
    fig5 = px.bar(
        x=mo_data['labels'], y=mo_data['values'],
        template="plotly_dark", color_discrete_sequence=['#D2991F']
    )
    fig5.update_layout(
        paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
        xaxis_title="Month", yaxis_title="Total Fatalities (All Time)"
    )
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("Insufficient data for monthly seasonality.")
