"""
Report Generator — Sentinel AI V2.0
Generates professional multi-section intelligence reports.
Supports Markdown and PDF output.
"""
import os
import json
from loguru import logger
from services.llm_service import LLMService
from utils.config import settings
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        self.llm = LLMService()

    def generate_full_report(self, query: str, risk_assessment: dict, incidents: list) -> str:
        """
        Generate a comprehensive professional intelligence report.
        Includes all sections: executive summary, threat assessment, evidence,
        historical analysis, statistics, recommendations, and references.
        """
        logger.info(f"Generating V2.0 intelligence report for: {query}")

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        report_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        risk_level = risk_assessment.get('risk_level', 'UNKNOWN')
        confidence = risk_assessment.get('confidence', 0) * 100
        risk_score = risk_assessment.get('risk_score', 0)
        reasoning = risk_assessment.get('reasoning', [])
        risk_factors = risk_assessment.get('risk_factors', [])
        recommendations = risk_assessment.get('strategic_recommendations', [])
        regional_stats = risk_assessment.get('regional_statistics', {})
        regional_trend = risk_assessment.get('regional_trend', 'Insufficient data')
        historical_evidence = risk_assessment.get('historical_evidence', [])
        ml_importance = risk_assessment.get('ml_feature_importance', {})

        # Generate executive summary via LLM
        exec_summary = self.llm.generate_report_summary(query, risk_assessment, incidents)

        # ─────────────────────────────────────────────────────────────
        # Build Report
        # ─────────────────────────────────────────────────────────────
        md = f"""# 🛡️ SENTINEL AI — INTELLIGENCE BRIEFING REPORT
---
**Classification:** INTERNAL INTELLIGENCE USE  
**Report ID:** {report_id}  
**Generated:** {now}  
**System:** Sentinel AI Version 2.0  

---

## SECTION 1 — EXECUTIVE SUMMARY

**Subject:** {query}

{exec_summary}

---

## SECTION 2 — THREAT & RISK ASSESSMENT

| Parameter | Value |
|-----------|-------|
| **Overall Risk Level** | {risk_level} |
| **Composite Risk Score** | {risk_score}/100 |
| **Model Confidence** | {confidence:.1f}% |
| **Regional Trend** | {regional_trend} |
| **Fatality Assessment** | {risk_assessment.get('fatality_assessment', 'Unknown')} |

### 2.1 Analytic Reasoning

"""
        for reason in reasoning:
            md += f"- {reason}\n"

        md += "\n### 2.2 Contributing Risk Factors\n\n"
        for factor in risk_factors:
            md += f"- **{factor}**\n"

        if ml_importance:
            md += "\n### 2.3 ML Feature Importance\n\n"
            md += "| Feature | Importance |\n|---------|------------|\n"
            for feat, val in sorted(ml_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
                md += f"| {feat} | {val:.4f} |\n"

        md += f"""
---

## SECTION 3 — REGIONAL INTELLIGENCE ANALYSIS

**Region of Interest:** {risk_assessment.get('regional_statistics', {}).get('total_in_region', 'N/A')} recorded incidents

| Metric | Value |
|--------|-------|
| Total Incidents in Region | {regional_stats.get('total_in_region', 'N/A')} |
| Recent (2yr) Incidents | {regional_stats.get('recent_2yr_in_region', 'N/A')} |
| Total in Country | {regional_stats.get('total_in_country', 'N/A')} |
| Regional Fatalities (all-time) | {regional_stats.get('regional_fatalities', 'N/A')} |
| Regional Share of Global Incidents | {regional_stats.get('regional_frequency_pct', 'N/A')}% |

**Regional Trend Assessment:** {regional_trend}

---

## SECTION 4 — HISTORICAL EVIDENCE

"""
        if incidents:
            md += f"**{len(incidents)} relevant incidents retrieved from intelligence database:**\n\n"
            for i, inc in enumerate(incidents[:10], 1):
                md += f"### Incident {i}: {inc.get('date', 'Unknown Date')} — {inc.get('country', inc.get('region', 'Unknown'))}\n\n"
                md += f"- **Attack Type:** {inc.get('attack_type', 'Unknown')}\n"
                md += f"- **Fatalities:** {inc.get('fatalities', 0)}\n"
                md += f"- **Source Dataset:** {inc.get('source_dataset', 'Historical')}\n"
                md += f"- **Similarity Score:** {inc.get('distance', inc.get('similarity', 0))*100:.1f}%\n"
                md += f"- **Summary:** {str(inc.get('summary', 'No summary available.'))[:400]}\n\n"
        else:
            md += "*No highly relevant historical incidents retrieved for this specific query.*\n\n"

        if historical_evidence:
            md += "**Top Matching Evidence from Risk Engine:**\n\n"
            for ev in historical_evidence[:3]:
                md += f"- **{ev.get('date')} | {ev.get('country')}** — {str(ev.get('summary', ''))[:200]} *(Similarity: {ev.get('similarity', 0):.0f}%)*\n"

        md += f"""
---

## SECTION 5 — STRATEGIC RECOMMENDATIONS

"""
        for rec in recommendations:
            md += f"{rec}\n\n"

        md += f"""
---

## SECTION 6 — FUTURE MONITORING PRIORITIES

Based on this assessment, the following monitoring priorities are recommended:

1. **Primary Focus:** Continue intelligence collection for {query[:50]}
2. **Secondary Focus:** Monitor escalation indicators in adjacent regions
3. **Reporting Cadence:** {"Daily" if risk_level in ["CRITICAL", "HIGH"] else "Weekly"} intelligence updates recommended
4. **Review Timeline:** Reassess threat assessment in {"48-72 hours" if risk_level == "CRITICAL" else "7 days" if risk_level == "HIGH" else "30 days"}

---

## REFERENCES

- **Primary Datasets:** Global Terrorism Database (GTD), ACLED
- **AI System:** Sentinel AI Version 2.0
- **ML Model:** Random Forest Classifier (multi-factor threat assessment)
- **Retrieval Method:** FAISS semantic vector search
- **Embedding Model:** {settings.EMBEDDING_MODEL_NAME}

---
*This report was generated automatically by Sentinel AI V2.0 for internal intelligence use.*  
*Validate all findings against primary sources before operational use.*
"""
        return md

    def save_report_markdown(self, markdown_content: str, filename: str) -> str:
        """Save report as Markdown file."""
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(settings.REPORTS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Markdown report saved: {filepath}")
        return filepath

    def save_report_pdf(self, markdown_content: str, filename: str) -> str:
        """Generate PDF from markdown content."""
        pdf_filename = filename.replace('.md', '.pdf')
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(settings.REPORTS_DIR, pdf_filename)

        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.set_margins(20, 20, 20)
            pdf.add_page()

            # Title
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 10, "SENTINEL AI — INTELLIGENCE BRIEFING REPORT", ln=True, align='C')
            pdf.set_font("Helvetica", '', 10)
            pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align='C')
            pdf.ln(5)

            # Content — strip markdown for PDF
            pdf.set_font("Helvetica", '', 10)
            lines = markdown_content.split('\n')
            for line in lines:
                # Format headers
                if line.startswith('## ') or line.startswith('# '):
                    pdf.set_font("Helvetica", 'B', 12)
                    clean = line.lstrip('#').strip()
                    pdf.ln(4)
                    try:
                        pdf.multi_cell(0, 8, clean, align='L')
                    except Exception:
                        pdf.multi_cell(0, 8, clean.encode('ascii', errors='replace').decode(), align='L')
                    pdf.set_font("Helvetica", '', 10)
                elif line.startswith('### '):
                    pdf.set_font("Helvetica", 'B', 11)
                    clean = line.lstrip('#').strip()
                    try:
                        pdf.multi_cell(0, 7, clean, align='L')
                    except Exception:
                        pdf.multi_cell(0, 7, clean.encode('ascii', errors='replace').decode(), align='L')
                    pdf.set_font("Helvetica", '', 10)
                elif line.strip() == '---':
                    pdf.ln(2)
                    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
                    pdf.ln(3)
                else:
                    # Strip markdown formatting
                    clean = line.replace('**', '').replace('*', '').replace('`', '')
                    clean = clean.replace('🛡️', '[SENTINEL]').replace('⚠️', '[WARNING]')
                    clean = clean.replace('🔴', '[CRITICAL]').replace('🟠', '[HIGH]')
                    clean = clean.replace('🟡', '[ELEVATED]').replace('🟢', '[LOW]')
                    clean = clean.replace('🔍', '[SEARCH]').replace('📊', '[ANALYTICS]')
                    if clean.strip():
                        try:
                            pdf.multi_cell(0, 6, clean, align='L')
                        except Exception:
                            pdf.multi_cell(0, 6, clean.encode('ascii', errors='replace').decode(), align='L')

            pdf.output(filepath)
            logger.info(f"PDF report saved: {filepath}")

        except Exception as e:
            logger.error(f"PDF generation failed: {e}. Saving as text fallback.")
            filepath = filepath.replace('.pdf', '_fallback.txt')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

        return filepath

    # Keep backward-compatible method
    def generate_pdf_ready_markdown(self, query: str, risk_assessment: dict, incidents: list) -> str:
        return self.generate_full_report(query, risk_assessment, incidents)
