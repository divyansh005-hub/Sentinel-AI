import streamlit as st
from frontend.theme import apply_theme, risk_badge
from frontend.components.widgets import render_risk_level_card, plot_feature_importance, render_incident_card, render_status_bar, plot_threat_probabilities
from frontend.api_client import predict_threat

st.set_page_config(page_title="Threat Assessment", page_icon="🎯", layout="wide")
apply_theme()
render_status_bar()

st.title("🎯 Risk Engine & Threat Assessment")
st.markdown("Evaluate hypothetical or upcoming operational scenarios using the multi-factor AI Risk Engine. Combines ML, heuristics, regional frequency, and RAG.")

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("### 📝 Operation Parameters")
    with st.form("risk_form"):
        region = st.selectbox("Region", [
            "Middle East & North Africa", "Sub-Saharan Africa", "South Asia", 
            "Southeast Asia", "Eastern Europe", "Western Europe", 
            "North America", "South America", "Central America & Caribbean"
        ])
        country = st.text_input("Country", value="Syria")
        attack_type = st.selectbox("Attack Type", [
            "Bombing/Explosion", "Armed Assault", "Assassination", 
            "Hostage Taking (Kidnapping)", "Hostage Taking (Barricade Incident)", 
            "Facility/Infrastructure Attack", "Explosions/Remote violence", "Battles"
        ])
        target_type = st.selectbox("Target Type", ["Military", "Police", "Civilians", "Government", "Infrastructure"])
        weapon_type = st.selectbox("Weapon Type", ["Explosives", "Firearms", "Melee", "Chemical", "Unknown"])
        
        col_f, col_i = st.columns(2)
        fatalities = col_f.number_input("Projected Fatalities", min_value=0, value=5)
        injuries = col_i.number_input("Projected Injuries", min_value=0, value=0)
        
        property_damage = st.number_input("Property Damage ($)", min_value=0.0, value=0.0, step=10000.0)
        
        submitted = st.form_submit_button("Run Risk Engine Analysis", use_container_width=True)

with c2:
    if submitted:
        payload = {
            "attack_type": attack_type,
            "target_type": target_type,
            "weapon_type": weapon_type,
            "region": region,
            "country": country,
            "fatalities": fatalities,
            "injuries": injuries,
            "property_damage": property_damage
        }
        
        with st.spinner("Processing through Multi-Factor Risk Engine..."):
            res = predict_threat(payload)
            
            if res:
                # ── Hero Metric ──
                render_risk_level_card(res['risk_level'], res['confidence'], res.get('risk_score', 0))
                
                st.markdown("---")
                
                # ── Analysis Tabs ──
                tab1, tab2, tab3 = st.tabs(["🧠 Analytic Reasoning", "📊 ML & Regional Data", "📚 Historical Evidence"])
                
                with tab1:
                    st.markdown(f"**Primary Action:** {res['monitoring_priority']}")
                    st.markdown("### Factor Analysis")
                    for factor in res.get('risk_factors', []):
                        st.markdown(f"- 🔸 **{factor}**")
                        
                    st.markdown("### Strategic Recommendations")
                    for rec in res.get('strategic_recommendations', []):
                        if "IMMEDIATE" in rec or "PRIORITY" in rec:
                            st.error(rec)
                        elif "WATCH" in rec:
                            st.warning(rec)
                        else:
                            st.info(rec)
                            
                with tab2:
                    col_ml, col_reg = st.columns(2)
                    with col_ml:
                        st.markdown("### ML Model Feature Importance")
                        if res.get('ml_feature_importance'):
                            st.plotly_chart(plot_feature_importance(res['ml_feature_importance']), use_container_width=True)
                        else:
                            st.info("ML model did not return feature importance.")
                            
                    with col_reg:
                        st.markdown("### Regional Intelligence")
                        reg_stats = res.get('regional_statistics', {})
                        trend = res.get('regional_trend', 'Unknown')
                        st.markdown(f"**Trend Assessment:** `{trend}`")
                        st.markdown(f"- Total Historical Incidents in Region: **{reg_stats.get('total_in_region', 0):,}**")
                        st.markdown(f"- Incidents in {country}: **{reg_stats.get('total_in_country', 0):,}**")
                        st.markdown(f"- Regional Share of Global Threat: **{reg_stats.get('regional_frequency_pct', 0)}%**")
                        
                with tab3:
                    incidents = res.get('supporting_incidents', [])
                    if incidents:
                        st.markdown(f"Retrieved **{len(incidents)}** highly relevant historical incidents matching this profile:")
                        for i, inc in enumerate(incidents):
                            render_incident_card(inc, i)
                    else:
                        st.info("No highly relevant historical incidents found in the intelligence database.")
    else:
        st.info("👈 Enter operation parameters and click **Run Risk Engine Analysis** to generate a threat assessment.")
        
        st.markdown("### Engine Capabilities")
        st.markdown("""
        The V2.0 Risk Engine combines multiple intelligence signals:
        1. **Machine Learning Base:** Random Forest Classifier trained on 200,000+ historical incidents.
        2. **Semantic Similarity:** FAISS vector retrieval of contextually similar events.
        3. **Regional Heuristics:** Statistical weighting based on regional conflict density.
        4. **Tactical Weighting:** Threat escalation based on attack vectors and projected casualties.
        """)
