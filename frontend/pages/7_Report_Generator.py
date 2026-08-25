import streamlit as st
import os
import base64
from frontend.theme import apply_theme
from frontend.components.widgets import render_status_bar
from frontend.api_client import generate_report

st.set_page_config(page_title="Report Generator", page_icon="📄", layout="wide")
apply_theme()
render_status_bar()

st.title("📄 Executive Report Generator")
st.markdown("Generate comprehensive intelligence briefings suitable for senior military leadership. Outputs formatted Markdown and PDF.")

# ── Report Generation Form ──────────────────────────────────────────────────
with st.container():
    st.markdown("### Report Parameters")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Intelligence Subject", placeholder="e.g. Assessment of recent IED attacks on infrastructure in South Asia", label_visibility="collapsed")
    with col2:
        top_k = st.number_input("Evidence Depth (Incidents)", min_value=3, max_value=20, value=5)
        
    generate_btn = st.button("Generate Intelligence Report", use_container_width=True)

st.markdown("---")

# ── Report Result ───────────────────────────────────────────────────────────
if generate_btn:
    if query:
        with st.spinner("Generating executive report (this may take up to 60 seconds)..."):
            res = generate_report(query=query, top_k=top_k)
            
            if res and "markdown_report" in res:
                st.success("Report generated successfully.")
                
                # Show Markdown
                with st.expander("Preview Report", expanded=True):
                    st.markdown(res["markdown_report"])
                    
                # Download Links
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    # Markdown Download
                    b64_md = base64.b64encode(res["markdown_report"].encode()).decode()
                    href_md = f'<a href="data:file/markdown;base64,{b64_md}" download="Sentinel_Intelligence_Report.md" target="_blank" style="display: block; text-align: center; background-color: #1B3A6B; color: white; padding: 10px; text-decoration: none; border-radius: 5px; font-weight: bold;">Download Markdown (.md)</a>'
                    st.markdown(href_md, unsafe_allow_html=True)
                    
                with col_dl2:
                    # PDF Download (if file exists on backend, we need to read it. Since we are in the same local FS, we can read it directly for download)
                    pdf_path = res.get("file_path")
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Sentinel_Intelligence_Report.pdf" target="_blank" style="display: block; text-align: center; background-color: #F85149; color: white; padding: 10px; text-decoration: none; border-radius: 5px; font-weight: bold;">Download PDF (.pdf)</a>'
                        st.markdown(href_pdf, unsafe_allow_html=True)
                    else:
                        st.warning("PDF generation failed on backend. Markdown format available.")
            else:
                st.error("Report generation failed.")
    else:
        st.error("Please enter an intelligence subject.")
else:
    st.info("Enter an intelligence subject to generate a multi-section executive briefing.")
    
    st.markdown("### Report Structure")
    st.markdown("""
    1. **Executive Summary:** High-level overview synthesized by AI Copilot.
    2. **Threat Assessment:** Risk level, confidence, and primary reasoning.
    3. **Regional Analysis:** Statistical breakdown of the target region.
    4. **Historical Evidence:** Top relevant incidents from the intelligence database.
    5. **Strategic Recommendations:** Actionable guidance based on risk level.
    6. **Monitoring Priorities:** Future intelligence collection requirements.
    """)
