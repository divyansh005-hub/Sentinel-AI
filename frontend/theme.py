import streamlit as st


def apply_theme():
    """Apply Sentinel AI V2.0 professional military dark theme."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Base ─────────────────────────────────────────── */
        .stApp {
            background-color: #080C14;
            color: #C9D1D9;
            font-family: 'Inter', sans-serif;
        }

        /* ── Sidebar ──────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D1117 0%, #0A0F1A 100%);
            border-right: 1px solid #1C2333;
        }

        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: #58A6FF;
        }

        /* ── Typography ───────────────────────────────────── */
        h1 {
            color: #E6EDF3 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        h2 {
            color: #58A6FF !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #1C2333;
            padding-bottom: 6px;
        }
        h3 {
            color: #79C0FF !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
        }

        /* ── Cards & Containers ───────────────────────────── */
        .stMetric {
            background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
            border: 1px solid #21262D;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .stMetric label {
            color: #8B949E !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stMetric [data-testid="metric-container"] > div > div {
            color: #E6EDF3 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        /* ── Buttons ──────────────────────────────────────── */
        .stButton > button {
            background: linear-gradient(135deg, #1B3A6B 0%, #1A4480 100%);
            color: #E6EDF3;
            border: 1px solid #388BFD;
            border-radius: 6px;
            padding: 8px 20px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.875rem;
            letter-spacing: 0.5px;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #264F8C 0%, #1F5299 100%);
            border-color: #58A6FF;
            box-shadow: 0 0 12px rgba(56, 139, 253, 0.3);
            transform: translateY(-1px);
        }

        /* ── Inputs & Selects ─────────────────────────────── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background-color: #0D1117 !important;
            border: 1px solid #30363D !important;
            border-radius: 6px !important;
            color: #C9D1D9 !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #388BFD !important;
            box-shadow: 0 0 0 2px rgba(56, 139, 253, 0.15) !important;
        }

        /* ── Alerts / Info Boxes ──────────────────────────── */
        .stAlert {
            border-radius: 6px;
            border-left: 4px solid;
        }

        /* ── Tabs ─────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #0D1117;
            border-bottom: 1px solid #21262D;
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #8B949E;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #58A6FF !important;
            border-bottom: 2px solid #388BFD !important;
            background-color: #161B22 !important;
        }

        /* ── Progress Bar ─────────────────────────────────── */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #1B3A6B, #58A6FF);
            border-radius: 4px;
        }

        /* ── Expanders ────────────────────────────────────── */
        .streamlit-expanderHeader {
            background-color: #161B22 !important;
            border: 1px solid #21262D !important;
            border-radius: 6px !important;
            color: #C9D1D9 !important;
        }

        /* ── Separator ────────────────────────────────────── */
        hr {
            border-color: #21262D;
            margin: 24px 0;
        }

        /* ── Chat Messages ────────────────────────────────── */
        [data-testid="chat-message-content"] {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
        }

        /* ── Code / Monospace ─────────────────────────────── */
        code {
            font-family: 'JetBrains Mono', monospace;
            background-color: #161B22;
            border: 1px solid #21262D;
            border-radius: 4px;
            padding: 1px 4px;
            color: #79C0FF;
        }

        /* ── Dataframes ───────────────────────────────────── */
        .stDataFrame {
            border: 1px solid #21262D;
            border-radius: 8px;
        }

        /* ── Status Badges ────────────────────────────────── */
        .sentinel-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .badge-critical { background: rgba(248,81,73,0.15); color: #F85149; border: 1px solid #F85149; }
        .badge-high     { background: rgba(219,76,7,0.15);  color: #DB4C07; border: 1px solid #DB4C07; }
        .badge-elevated { background: rgba(210,153,34,0.15);color: #D2991F; border: 1px solid #D2991F; }
        .badge-low      { background: rgba(63,185,80,0.15); color: #3FB950; border: 1px solid #3FB950; }

        /* ── Scrollbar ────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0D1117; }
        ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #58A6FF; }
        </style>
    """, unsafe_allow_html=True)


def risk_badge(level: str) -> str:
    """Return HTML badge for a risk level."""
    colors = {
        "CRITICAL": ("#F85149", "#3D0B0B"),
        "HIGH": ("#DB4C07", "#3D1A00"),
        "ELEVATED": ("#D2991F", "#3D2D00"),
        "LOW": ("#3FB950", "#0B2E14"),
    }
    fg, bg = colors.get(level.upper(), ("#8B949E", "#161B22"))
    return (
        f'<span style="background:{bg}; color:{fg}; border:1px solid {fg}; '
        f'padding:4px 12px; border-radius:12px; font-size:0.8rem; '
        f'font-weight:700; letter-spacing:1px;">{level}</span>'
    )


def status_indicator(online: bool = True) -> str:
    """Return HTML status indicator."""
    if online:
        return '<span style="color:#3FB950; font-size:0.75rem;">● ONLINE</span>'
    return '<span style="color:#F85149; font-size:0.75rem;">● OFFLINE</span>'
