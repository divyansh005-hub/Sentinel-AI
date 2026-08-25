import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
from frontend.theme import apply_theme
from frontend.components.widgets import render_status_bar
from frontend.api_client import get_analytics

st.set_page_config(page_title="Intelligence Map", page_icon="🗺️", layout="wide")
apply_theme()
render_status_bar()

st.title("🗺️ Geographic Intelligence Map")
st.markdown("Global distribution of threat incidents. Clustered for performance with heatmap overlays.")

with st.spinner("Loading geographic data..."):
    # Fetch sampled geographic data for map (up to 5000 points to prevent browser crash)
    geo_data = get_analytics("heatmap_data")
    
    if geo_data and "points" in geo_data and geo_data["points"]:
        points = geo_data["points"]
        st.success(f"Loaded {len(points)} geographic data points.")
        
        # Options
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("### Map Layers")
            show_clusters = st.checkbox("Show Incident Clusters", value=True)
            show_heatmap = st.checkbox("Show Heatmap Overlay", value=False)
            
            st.markdown("### Legend")
            st.markdown("🔴 High Fatalities (>= 10)")
            st.markdown("🟠 Elevated Fatalities (1 - 9)")
            st.markdown("🟢 Minimal/No Fatalities")
        
        with col2:
            # Initialize map centered generally
            m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
            
            if show_heatmap:
                # Add HeatMap
                heat_data = [[p['latitude'], p['longitude'], p.get('fatalities', 1)] for p in points]
                HeatMap(heat_data, radius=15, blur=20, max_zoom=1).add_to(m)
                
            if show_clusters:
                # Add MarkerCluster
                marker_cluster = MarkerCluster().add_to(m)
                
                for p in points:
                    fat = p.get('fatalities', 0)
                    if fat >= 10:
                        color = 'red'
                    elif fat > 0:
                        color = 'orange'
                    else:
                        color = 'green'
                        
                    # Create popup HTML
                    popup_html = f"""
                    <div style="font-family:sans-serif; width:200px;">
                        <b>Date:</b> {p.get('date', 'Unknown')}<br>
                        <b>Country:</b> {p.get('country', 'Unknown')}<br>
                        <b>Attack:</b> {p.get('attack_type', 'Unknown')}<br>
                        <b>Fatalities:</b> {fat}<br>
                    </div>
                    """
                    
                    folium.CircleMarker(
                        location=[p['latitude'], p['longitude']],
                        radius=6,
                        popup=folium.Popup(popup_html, max_width=250),
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7
                    ).add_to(marker_cluster)
            
            # Render map
            st_folium(m, width=1200, height=600, returned_objects=[])
    else:
        st.warning("No geographic data available. Ensure dataset contains valid latitude/longitude coordinates.")
