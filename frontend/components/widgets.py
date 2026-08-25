import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render_metric_card(title: str, value: str, delta: str = None, color: str = "#E6EDF3", icon: str = ""):
    """Render a styled metric card."""
    delta_html = ""
    if delta:
        delta_color = "#3FB950" if not delta.startswith("-") else "#F85149"
        delta_html = f'<p style="margin:0; color:{delta_color}; font-size:0.75rem;">{delta}</p>'

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
            border: 1px solid #21262D;
            border-radius: 8px;
            padding: 16px 20px;
            height: 100%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">
            <p style="margin:0 0 4px 0; color:#8B949E; font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;">{icon} {title}</p>
            <h2 style="margin:0; color:{color}; font-size:1.8rem; font-weight:700; line-height:1.2;">{value}</h2>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def render_risk_level_card(risk_level: str, confidence: float, score: int = 0):
    """Render a prominent risk level display card."""
    colors = {
        "CRITICAL": ("#F85149", "#3D0B0B"),
        "HIGH": ("#DB4C07", "#3D1A00"),
        "ELEVATED": ("#D2991F", "#3D2D00"),
        "LOW": ("#3FB950", "#0B2E14"),
    }
    fg, bg = colors.get(risk_level.upper(), ("#8B949E", "#161B22"))

    st.markdown(f"""
        <div style="
            background: {bg};
            border: 2px solid {fg};
            border-radius: 10px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 0 20px {fg}33;
        ">
            <p style="margin:0; color:{fg}; font-size:0.75rem; text-transform:uppercase; letter-spacing:3px; font-weight:600;">THREAT ASSESSMENT</p>
            <h1 style="margin:8px 0; color:{fg}; font-size:3rem; font-weight:800; letter-spacing:2px;">{risk_level}</h1>
            <p style="margin:0; color:{fg}99; font-size:0.875rem;">
                Confidence: <b>{confidence*100:.1f}%</b> | Risk Score: <b>{score}/100</b>
            </p>
        </div>
    """, unsafe_allow_html=True)


def plot_feature_importance(importance_dict: dict) -> go.Figure:
    """Plot ML feature importance as horizontal bar chart."""
    if not importance_dict:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", title="No feature importance available")
        return fig

    sorted_items = sorted(importance_dict.items(), key=lambda x: x[1], reverse=False)
    features = [item[0].replace('_', ' ').title() for item in sorted_items]
    values = [item[1] for item in sorted_items]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker=dict(
            color=values,
            colorscale=[[0, '#1B3A6B'], [0.5, '#388BFD'], [1, '#79C0FF']],
            showscale=False
        ),
        text=[f"{v:.3f}" for v in values],
        textposition='outside',
    ))
    fig.update_layout(
        title=dict(text="Contributing Risk Features", font=dict(color='#E6EDF3', size=14)),
        template="plotly_dark",
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        xaxis=dict(showgrid=True, gridcolor='#21262D', color='#8B949E'),
        yaxis=dict(showgrid=False, color='#C9D1D9'),
        margin=dict(l=10, r=60, t=40, b=10),
        height=250,
    )
    return fig


def plot_threat_probabilities(probs: dict) -> go.Figure:
    """Plot threat level probability distribution."""
    level_colors = {
        'LOW': '#3FB950',
        'MEDIUM': '#D2991F',
        'HIGH': '#F85149',
        'CRITICAL': '#FF0000'
    }
    labels = list(probs.keys())
    values = list(probs.values())
    colors = [level_colors.get(l.upper(), '#8B949E') for l in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{v*100:.1f}%" for v in values],
        textposition='outside',
    ))
    fig.update_layout(
        title=dict(text="Threat Level Probability Distribution", font=dict(color='#E6EDF3', size=14)),
        template="plotly_dark",
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        yaxis=dict(
            title="Probability", showgrid=True, gridcolor='#21262D',
            color='#8B949E', tickformat='.0%', range=[0, max(values)*1.3 if values else 1]
        ),
        xaxis=dict(color='#C9D1D9'),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def render_incident_card(incident: dict, idx: int = 0):
    """Render a styled incident card in an expander."""
    date = incident.get('date', 'Unknown')
    country = incident.get('country', 'Unknown')
    region = incident.get('region', 'Unknown')
    attack = incident.get('attack_type', 'Unknown')
    fatalities = incident.get('fatalities', 0)
    similarity = float(incident.get('distance', 0)) * 100
    summary = incident.get('summary', 'No summary available.')
    source = incident.get('source_dataset', 'Historical')

    # Choose color for fatality count
    if fatalities >= 20:
        fat_color = "#F85149"
    elif fatalities >= 5:
        fat_color = "#D2991F"
    else:
        fat_color = "#3FB950"

    label = f"#{idx+1} | {date} | {country} | {attack} | Similarity: {similarity:.0f}%"
    with st.expander(label, expanded=(idx == 0)):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**📅 Date:** {date}")
            st.markdown(f"**🌍 Location:** {country}, {region}")
        with col2:
            st.markdown(f"**⚔️ Attack Type:** {attack}")
            st.markdown(f"**🔫 Weapon:** {incident.get('weapon_type', 'Unknown')}")
        with col3:
            st.markdown(f"**💀 Fatalities:** <span style='color:{fat_color};font-weight:700;'>{fatalities}</span>", unsafe_allow_html=True)
            st.markdown(f"**📊 Source:** `{source}`")
        st.markdown(f"**📝 Summary:** {summary[:400]}")
        st.markdown(f"*Semantic Similarity: {similarity:.1f}%*")


def render_status_bar():
    """Render the system status bar."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    st.markdown(f"""
        <div style="
            background: #0D1117;
            border: 1px solid #21262D;
            border-radius: 6px;
            padding: 8px 16px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #8B949E;
        ">
            <span>🛡️ <b style="color:#58A6FF;">SENTINEL AI</b> v2.0 | Status: <span style="color:#3FB950;">● OPERATIONAL</span></span>
            <span>Risk Engine: <span style="color:#3FB950;">● ACTIVE</span> | RAG: <span style="color:#3FB950;">● CONNECTED</span> | {now}</span>
        </div>
    """, unsafe_allow_html=True)
