import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import streamlit as st
import pandas as pd
from frontend.theme import apply_theme, risk_badge
from frontend.components.widgets import render_status_bar
from frontend.api_client import search_incidents

st.set_page_config(page_title="Incident Explorer", page_icon="🔍", layout="wide")
apply_theme()
render_status_bar()

st.title("🔍 Semantic Incident Explorer")
st.markdown("Perform deep vector searches across the global intelligence database (GTD + ACLED) using natural language.")

# ── Search Interface ────────────────────────────────────────────────────────
with st.container():
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input("Intelligence Query", placeholder="e.g. Suicide bombings targeting police checkpoints in South Asia...", label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("🔎 Run Search", use_container_width=True)

# ── Filters ─────────────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced Filters", expanded=False):
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        country_filter = st.text_input("Country")
    with f_col2:
        region_filter = st.text_input("Region")
    with f_col3:
        attack_filter = st.text_input("Attack Type")
    with f_col4:
        c_yr1, c_yr2 = st.columns(2)
        year_from = c_yr1.number_input("Year From", min_value=1970, max_value=2026, value=None, step=1)
        year_to = c_yr2.number_input("Year To", min_value=1970, max_value=2026, value=None, step=1)
        
    top_k = st.slider("Max Results to Retrieve", min_value=5, max_value=50, value=15)

st.markdown("---")

# ── Results ─────────────────────────────────────────────────────────────────
if search_clicked:
    if query:
        with st.spinner("Searching FAISS vector space..."):
            results = search_incidents(
                query=query, 
                top_k=top_k,
                country=country_filter if country_filter else None,
                region=region_filter if region_filter else None,
                attack_type=attack_filter if attack_filter else None,
                year_from=year_from if year_from else None,
                year_to=year_to if year_to else None
            )
            
            if results:
                st.success(f"Retrieved {len(results)} highly relevant intelligence records.")
                
                # Tabular view option
                tab1, tab2 = st.tabs(["📝 Detailed View", "📊 Table View"])
                
                with tab1:
                    for i, res in enumerate(results):
                        fat = res.get('fatalities', 0)
                        fat_color = "#F85149" if fat >= 5 else "#3FB950"
                        sim = float(res.get('distance', 0)) * 100
                        
                        with st.container():
                            st.markdown(f"""
                            <div style="background:#0D1117; border:1px solid #21262D; border-radius:6px; padding:16px; margin-bottom:12px;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                                    <h4 style="margin:0; color:#58A6FF;">{res.get('date')} | {res.get('city')}, {res.get('country')}</h4>
                                    <span style="background:#161B22; border:1px solid #30363D; padding:2px 8px; border-radius:12px; font-size:0.8rem; color:#79C0FF;">Relevance: {sim:.1f}%</span>
                                </div>
                                <div style="display:flex; gap:20px; margin-bottom:12px; font-size:0.9rem;">
                                    <span><b>Type:</b> {res.get('attack_type')}</span>
                                    <span><b>Fatalities:</b> <span style="color:{fat_color}; font-weight:700;">{fat}</span></span>
                                    <span><b>Source:</b> <code style="color:#C9D1D9;">{res.get('source_dataset')}</code></span>
                                </div>
                                <p style="margin:0; color:#8B949E; font-size:0.95rem; line-height:1.5;">{res.get('summary')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                with tab2:
                    # Flatten for table
                    df = pd.DataFrame(results)
                    if not df.empty:
                        # Reorder and format
                        df['similarity'] = (df['distance'].astype(float) * 100).round(1).astype(str) + '%'
                        cols = ['date', 'country', 'city', 'attack_type', 'fatalities', 'similarity', 'source_dataset']
                        cols = [c for c in cols if c in df.columns]
                        st.dataframe(df[cols], use_container_width=True, hide_index=True)
            else:
                st.warning("No incidents matched your query and filters. Try broadening your search.")
    else:
        st.error("Please enter an intelligence query.")
else:
    st.info("Enter a semantic query to explore historical intelligence. The system understands context, not just keywords.")
    
    st.markdown("### Example Queries")
    st.markdown("- *IED attacks targeting military convoys in the Middle East*")
    st.markdown("- *Assassinations of government officials involving firearms*")
    st.markdown("- *Mass casualty events at civilian infrastructure*")
