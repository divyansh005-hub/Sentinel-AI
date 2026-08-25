"""
Upgraded Risk Engine — Sentinel AI V2.0
Multi-factor threat assessment combining:
  - ML prediction
  - Historical similarity (RAG)
  - Regional incident frequency
  - Fatality trend analysis
  - Optional live intelligence context
Returns full explainable assessment.
"""
import pandas as pd
import os
from loguru import logger
from services.prediction_service import PredictionService
from utils.constants import RISK_LEVELS, ATTACK_RISK_WEIGHTS, HIGH_RISK_REGIONS
from utils.config import settings


class RiskEngine:
    """
    The Intelligence Brain — V2.0.
    Combines ML prediction with historical statistics for explainable assessments.
    """

    def __init__(self):
        self.predictor = PredictionService()
        self._stats_cache = None

    def _load_regional_stats(self) -> dict:
        """Load pre-computed regional statistics from unified dataset."""
        if self._stats_cache is not None:
            return self._stats_cache

        stats = {}
        try:
            if os.path.exists(settings.UNIFIED_DATASET_PATH):
                df = pd.read_parquet(settings.UNIFIED_DATASET_PATH)
                region_counts = df['region'].value_counts().to_dict()
                country_counts = df['country'].value_counts().to_dict()
                region_fatalities = df.groupby('region')['fatalities'].sum().to_dict()
                
                # Recent 2 years trend
                df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
                max_year = df['year'].max()
                recent = df[df['year'] >= (max_year - 2)] if pd.notna(max_year) else df
                recent_counts = recent['region'].value_counts().to_dict()
                
                stats = {
                    'region_incident_counts': region_counts,
                    'country_incident_counts': country_counts,
                    'region_fatalities': region_fatalities,
                    'recent_region_counts': recent_counts,
                    'total_incidents': len(df),
                }
                self._stats_cache = stats
        except Exception as e:
            logger.warning(f"Could not load regional stats: {e}")

        return stats

    def evaluate_risk(self, incident_data: dict, historical_context: list = None) -> dict:
        """
        Full multi-factor risk evaluation.
        Returns rich explainable assessment.
        """
        logger.info(f"V2.0 Risk evaluation for: {incident_data.get('country')} | {incident_data.get('attack_type')}")

        # ── 1. ML Prediction ──────────────────────────────────────────
        ml_result = self.predictor.predict(incident_data)
        if "error" in ml_result:
            # Degrade gracefully — use heuristic assessment
            return self._heuristic_assessment(incident_data, historical_context, error=ml_result["error"])

        ml_threat = ml_result['threat_level']
        ml_confidence = ml_result['confidence']
        ml_importance = ml_result.get('feature_importance', {})

        # ── 2. Historical Similarity Analysis ────────────────────────
        historical_count = len(historical_context) if historical_context else 0
        historical_evidence = []
        for inc in (historical_context or []):
            historical_evidence.append({
                "date": inc.get("date"),
                "country": inc.get("country", "Unknown"),
                "region": inc.get("region", "Unknown"),
                "summary": inc.get("summary", "")[:200],
                "fatalities": inc.get("fatalities", 0),
                "similarity": round(float(inc.get("distance", 0)) * 100, 1),
                "source": inc.get("source_dataset", "Historical"),
            })

        # ── 3. Regional Frequency Factor ─────────────────────────────
        stats = self._load_regional_stats()
        region = incident_data.get('region', 'Unknown')
        country = incident_data.get('country', 'Unknown')
        region_count = stats.get('region_incident_counts', {}).get(region, 0)
        total_incidents = stats.get('total_incidents', 1)
        regional_frequency_pct = round((region_count / max(total_incidents, 1)) * 100, 1)
        
        recent_region_count = stats.get('recent_region_counts', {}).get(region, 0)
        country_count = stats.get('country_incident_counts', {}).get(country, 0)
        region_fatalities = stats.get('region_fatalities', {}).get(region, 0)

        # ── 4. Attack Type Risk Weight ────────────────────────────────
        attack_type = incident_data.get('attack_type', 'Unknown')
        attack_weight = ATTACK_RISK_WEIGHTS.get(attack_type, 1.0)

        # ── 5. Fatality Assessment ────────────────────────────────────
        projected_fatalities = int(incident_data.get('fatalities', 0))
        fatality_factor = "MINIMAL"
        if projected_fatalities >= 50:
            fatality_factor = "MASS CASUALTY"
        elif projected_fatalities >= 20:
            fatality_factor = "SEVERE"
        elif projected_fatalities >= 5:
            fatality_factor = "SIGNIFICANT"

        # ── 6. Composite Risk Level Determination ────────────────────
        risk_score = 0
        reasoning = []
        risk_factors = []

        # ML base
        if ml_threat == "HIGH":
            risk_score += 40
            reasoning.append(f"ML threat model predicts HIGH threat ({ml_confidence*100:.0f}% confidence).")
            risk_factors.append(f"Model Prediction: HIGH ({ml_confidence*100:.0f}%)")
        elif ml_threat == "MEDIUM":
            risk_score += 20
            reasoning.append(f"ML threat model predicts MEDIUM threat ({ml_confidence*100:.0f}% confidence).")
            risk_factors.append(f"Model Prediction: MEDIUM ({ml_confidence*100:.0f}%)")
        else:
            risk_score += 5
            reasoning.append(f"ML threat model predicts LOW threat ({ml_confidence*100:.0f}% confidence).")
            risk_factors.append(f"Model Prediction: LOW ({ml_confidence*100:.0f}%)")

        # Historical similarity
        if historical_count >= 3:
            risk_score += 20
            reasoning.append(f"High historical similarity: {historical_count} closely matched incidents in intelligence database.")
            risk_factors.append(f"Historical Similarity: {historical_count} matching incidents")
        elif historical_count >= 1:
            risk_score += 10
            reasoning.append(f"Moderate historical similarity: {historical_count} relevant incident(s) retrieved.")
            risk_factors.append(f"Historical Similarity: {historical_count} matching incidents")

        # Regional frequency
        if region in HIGH_RISK_REGIONS or regional_frequency_pct > 10:
            risk_score += 15
            reasoning.append(f"High-frequency conflict region: {region} accounts for {regional_frequency_pct:.1f}% of all recorded incidents.")
            risk_factors.append(f"Regional Frequency: {regional_frequency_pct:.1f}% global share")
        elif regional_frequency_pct > 5:
            risk_score += 8
            reasoning.append(f"Elevated regional activity: {region} ({regional_frequency_pct:.1f}% of incidents).")
            risk_factors.append(f"Regional Activity: {regional_frequency_pct:.1f}%")

        # Fatalities
        if projected_fatalities >= 20:
            risk_score += 20
            reasoning.append(f"Mass casualty projection: {projected_fatalities} projected fatalities forces critical escalation.")
            risk_factors.append(f"Projected Fatalities: {fatality_factor} ({projected_fatalities})")
        elif projected_fatalities >= 5:
            risk_score += 10
            reasoning.append(f"Significant casualty projection: {projected_fatalities} fatalities.")
            risk_factors.append(f"Projected Fatalities: {fatality_factor} ({projected_fatalities})")

        # Attack type weight
        if attack_weight >= 2.5:
            risk_score += 15
            reasoning.append(f"High-severity attack vector: {attack_type} (risk weight: {attack_weight}x).")
            risk_factors.append(f"Attack Vector: {attack_type} (weight {attack_weight}x)")
        elif attack_weight >= 1.5:
            risk_score += 8
            reasoning.append(f"Elevated attack type: {attack_type} (risk weight: {attack_weight}x).")

        # ── 7. Map Score to Risk Level ────────────────────────────────
        if risk_score >= 75:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "ELEVATED"
        else:
            risk_level = "LOW"

        monitoring_priority = RISK_LEVELS.get(risk_level, "Routine monitoring.")

        # ── 8. Strategic Recommendations ─────────────────────────────
        recommendations = self._generate_recommendations(
            risk_level, region, country, attack_type, projected_fatalities
        )

        # ── 9. Regional Trend ─────────────────────────────────────────
        trend = "Stable"
        if recent_region_count > (region_count * 0.6):
            trend = "Escalating — majority of incidents are recent"
        elif recent_region_count < (region_count * 0.2):
            trend = "Declining — low recent incident rate"

        return {
            "risk_level": risk_level,
            "confidence": round(ml_confidence, 4),
            "risk_score": risk_score,
            "explanation": " ".join(reasoning),
            "reasoning": reasoning,
            "risk_factors": risk_factors,
            "monitoring_priority": monitoring_priority,
            "strategic_recommendations": recommendations,
            "regional_trend": trend,
            "regional_statistics": {
                "total_in_region": region_count,
                "recent_2yr_in_region": recent_region_count,
                "total_in_country": country_count,
                "regional_fatalities": int(region_fatalities),
                "regional_frequency_pct": regional_frequency_pct,
            },
            "historical_evidence": historical_evidence,
            "fatality_assessment": fatality_factor,
            "ml_feature_importance": ml_importance,
            "supporting_incidents": historical_context if historical_context else [],
        }

    def _generate_recommendations(
        self, risk_level: str, region: str, country: str,
        attack_type: str, fatalities: int
    ) -> list:
        """Generate strategic recommendations based on assessed risk."""
        recs = []

        if risk_level == "CRITICAL":
            recs.append("🔴 IMMEDIATE ACTION: Deploy rapid response assets and notify command structure.")
            recs.append("Initiate full intelligence collection posture for the area of operation.")
            recs.append(f"Coordinate with regional intelligence partners in {region}.")
            recs.append("Prepare contingency plans for escalation scenarios.")
        elif risk_level == "HIGH":
            recs.append("🟠 PRIORITY ALERT: Escalate to senior intelligence staff for review.")
            recs.append(f"Increase monitoring frequency for {country} and adjacent regions.")
            recs.append("Review existing asset protection protocols for the target area.")
            recs.append("Prepare situational reports for daily command briefings.")
        elif risk_level == "ELEVATED":
            recs.append("🟡 WATCH STATUS: Maintain elevated situational awareness.")
            recs.append(f"Schedule increased intelligence collection activities in {region}.")
            recs.append("Brief relevant stakeholders on potential escalation pathways.")
        else:
            recs.append("🟢 ROUTINE: Continue standard monitoring protocol.")
            recs.append("Include in routine intelligence reporting cycle.")

        if 'Bombing' in attack_type or 'Explosion' in attack_type:
            recs.append("CBRN/IED assessment team should evaluate explosive device risk profile.")
        if fatalities >= 10:
            recs.append(f"Medical and emergency response assets should be placed on standby.")

        return recs

    def _heuristic_assessment(self, incident_data: dict, historical_context: list, error: str) -> dict:
        """Fallback heuristic assessment when ML model is unavailable."""
        logger.warning(f"Using heuristic assessment — ML error: {error}")

        fatalities = int(incident_data.get('fatalities', 0))
        attack_type = incident_data.get('attack_type', 'Unknown')
        attack_weight = ATTACK_RISK_WEIGHTS.get(attack_type, 1.0)

        score = (fatalities * 2) + (attack_weight * 5) + (len(historical_context or []) * 3)

        if score >= 30:
            risk_level = "HIGH"
        elif score >= 10:
            risk_level = "ELEVATED"
        else:
            risk_level = "LOW"

        reasoning = [
            f"⚠️ ML model unavailable ({error}). Using heuristic assessment.",
            f"Heuristic factors: {fatalities} projected fatalities, {attack_type} (weight {attack_weight}x).",
            f"Historical similarity: {len(historical_context or [])} matching incidents found.",
        ]

        return {
            "risk_level": risk_level,
            "confidence": 0.60,
            "risk_score": int(score),
            "explanation": " ".join(reasoning),
            "reasoning": reasoning,
            "risk_factors": [f"Heuristic Score: {score}", f"Attack Type: {attack_type}"],
            "monitoring_priority": RISK_LEVELS.get(risk_level, "Routine monitoring."),
            "strategic_recommendations": self._generate_recommendations(
                risk_level, incident_data.get('region', 'Unknown'),
                incident_data.get('country', 'Unknown'), attack_type, fatalities
            ),
            "regional_trend": "Data unavailable",
            "regional_statistics": {},
            "historical_evidence": [],
            "fatality_assessment": "SIGNIFICANT" if fatalities >= 5 else "MINIMAL",
            "ml_feature_importance": {},
            "supporting_incidents": historical_context if historical_context else [],
        }
