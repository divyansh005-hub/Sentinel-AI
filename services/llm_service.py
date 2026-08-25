"""
LLM Service — Sentinel AI V2.0
Upgraded intelligence copilot with:
  - Rich military-grade system prompts
  - Context-aware response generation
  - Support for Gemini AI + mock fallback
  - Live intelligence context integration
"""
from loguru import logger
from utils.config import settings
from datetime import datetime


SYSTEM_PROMPT = """You are SENTINEL, an elite AI Intelligence Analyst for a military decision support system.

Your role:
- Provide strategic, precise, and actionable military intelligence analysis
- Synthesize historical incident data with geopolitical context
- Identify patterns, threat trends, and operational risks
- Speak with authority, clarity, and professionalism

Response format:
- Lead with the most critical intelligence finding
- Support claims with evidence from retrieved incidents
- Provide specific, actionable recommendations
- Note limitations of analysis when applicable
- Use military terminology appropriately

Critical rules:
- Never make up incidents or statistics
- Always cite retrieved context when used
- If data is insufficient, state it clearly
- Distinguish between confirmed intelligence and analysis
"""


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = None

        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                if settings.GEMINI_API_KEY:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    self.model = genai.GenerativeModel(
                        'gemini-pro',
                        system_instruction=SYSTEM_PROMPT
                    )
                    logger.info("Gemini AI initialized for Sentinel V2.0.")
                else:
                    logger.warning("Gemini API key not configured. Using enhanced mock mode.")
                    self.provider = "mock"
            except ImportError:
                logger.error("google-generativeai not installed. Using enhanced mock mode.")
                self.provider = "mock"

    def ask(self, prompt: str, context: list = None, live_context: dict = None) -> str:
        """Single-turn intelligence query."""
        full_prompt = self._build_intelligence_prompt(prompt, context, live_context)
        return self._generate(full_prompt)

    def chat(self, query: str, history: list, context: list = None, live_context: dict = None) -> str:
        """Multi-turn conversational intelligence briefing."""
        # Build conversation context
        conv_context = ""
        if history:
            conv_context = "=== CONVERSATION HISTORY ===\n"
            for msg in history[-6:]:  # Last 3 exchanges
                role = msg.get("role", "user").upper()
                conv_context += f"{role}: {msg.get('content', '')}\n"
            conv_context += "\n"

        full_prompt = (
            f"{conv_context}"
            f"=== NEW INTELLIGENCE QUERY ===\n"
            f"{query}\n\n"
        )

        if context:
            full_prompt += self._format_historical_context(context)

        if live_context and live_context.get("items"):
            full_prompt += self._format_live_context(live_context)
        elif live_context:
            full_prompt += f"\n[INTEL SOURCE NOTE]: {live_context.get('disclaimer', '')}\n"

        full_prompt += "\nProvide a structured intelligence briefing with strategic assessment and recommendations."
        return self._generate(full_prompt)

    def generate_report_summary(self, query: str, risk_assessment: dict, incidents: list) -> str:
        """Generate executive summary for intelligence report."""
        prompt = f"""Generate a professional executive intelligence summary for the following assessment:

SUBJECT: {query}
RISK LEVEL: {risk_assessment.get('risk_level', 'UNKNOWN')}
CONFIDENCE: {risk_assessment.get('confidence', 0)*100:.0f}%
RISK SCORE: {risk_assessment.get('risk_score', 0)}/100

KEY FACTORS:
{chr(10).join(['- ' + r for r in risk_assessment.get('reasoning', [])[:3]])}

REGIONAL CONTEXT:
{str(risk_assessment.get('regional_statistics', {}))}

Write a 3-paragraph executive summary suitable for senior military leadership.
Paragraph 1: Situation Overview
Paragraph 2: Threat Assessment and Evidence
Paragraph 3: Strategic Recommendations
"""
        return self._generate(prompt)

    def answer_intelligence_question(self, query: str, context: list, live_context: dict = None) -> str:
        """Answer specific intelligence questions with retrieved context."""
        # Detect query intent for better responses
        query_lower = query.lower()

        if any(word in query_lower for word in ['summarize', 'summary', 'overview', 'brief']):
            intent_prefix = "Provide a comprehensive intelligence summary covering key incidents, trends, and threat patterns."
        elif any(word in query_lower for word in ['recent', 'latest', 'current', 'happened']):
            intent_prefix = "Focus on the most recent intelligence, chronological trends, and current threat status."
        elif any(word in query_lower for word in ['similar', 'comparable', 'historical', 'precedent']):
            intent_prefix = "Identify historical parallels, patterns of similarity, and precedents from the intelligence database."
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            intent_prefix = "Provide a structured comparative analysis with key differentiators and similarities."
        elif any(word in query_lower for word in ['region', 'monitor', 'priority', 'watch']):
            intent_prefix = "Assess monitoring priorities, risk rankings, and surveillance recommendations by region."
        elif any(word in query_lower for word in ['attack type', 'method', 'tactic', 'modus']):
            intent_prefix = "Analyze attack methodology, tactical patterns, and operational signatures."
        else:
            intent_prefix = "Provide a thorough intelligence analysis with supporting evidence."

        prompt = f"{intent_prefix}\n\nINTELLIGENCE QUERY: {query}\n\n"
        if context:
            prompt += self._format_historical_context(context)
        if live_context and live_context.get("items"):
            prompt += self._format_live_context(live_context)
        elif live_context:
            prompt += f"\n[NOTE]: {live_context.get('disclaimer', '')}\n"

        return self._generate(prompt)

    def _format_historical_context(self, context: list) -> str:
        """Format retrieved incidents as structured intelligence context."""
        if not context:
            return ""

        out = "=== RETRIEVED HISTORICAL INTELLIGENCE ===\n"
        for i, inc in enumerate(context[:8], 1):
            out += (
                f"[INCIDENT {i}]\n"
                f"  Date: {inc.get('date', 'Unknown')}\n"
                f"  Location: {inc.get('city', 'Unknown')}, {inc.get('country', inc.get('region', 'Unknown'))}\n"
                f"  Type: {inc.get('attack_type', 'Unknown')}\n"
                f"  Fatalities: {inc.get('fatalities', 0)}\n"
                f"  Source: {inc.get('source_dataset', 'Historical')}\n"
                f"  Summary: {str(inc.get('summary', ''))[:300]}\n"
                f"  Similarity: {inc.get('distance', 0)*100:.0f}%\n\n"
            )
        return out

    def _format_live_context(self, live_context: dict) -> str:
        """Format live intelligence items."""
        items = live_context.get("items", [])
        if not items:
            return ""

        out = "=== LIVE INTELLIGENCE FEED ===\n"
        for i, item in enumerate(items[:5], 1):
            out += (
                f"[LIVE INTEL {i}]\n"
                f"  Date: {item.get('date', 'Recent')}\n"
                f"  Source: {item.get('source', 'Live Feed')}\n"
                f"  Summary: {str(item.get('summary', ''))[:250]}\n\n"
            )
        return out

    def _build_intelligence_prompt(self, query: str, context: list, live_context: dict = None) -> str:
        """Build a complete intelligence analysis prompt."""
        prompt = f"INTELLIGENCE QUERY: {query}\n\n"
        if context:
            prompt += self._format_historical_context(context)
        if live_context and live_context.get("items"):
            prompt += self._format_live_context(live_context)
        elif live_context:
            prompt += f"\n[NOTE]: {live_context.get('disclaimer', '')}\n"
        return prompt

    def _generate(self, prompt: str) -> str:
        """Generate response using configured LLM provider."""
        if self.provider == "gemini" and self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Gemini API error: {e}. Falling back to enhanced mock.")
                return self._enhanced_mock_response(prompt)
        else:
            return self._enhanced_mock_response(prompt)

    def _enhanced_mock_response(self, prompt: str) -> str:
        """Enhanced mock response with intelligence-grade formatting."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        # Parse context from prompt to make mock more realistic
        has_context = "RETRIEVED HISTORICAL INTELLIGENCE" in prompt or "INCIDENT" in prompt
        has_live = "LIVE INTELLIGENCE FEED" in prompt
        has_history = "CONVERSATION HISTORY" in prompt

        if "CRITICAL" in prompt or "critical" in prompt.lower():
            threat_note = "⚠️ **CRITICAL THREAT INDICATORS PRESENT**. Immediate command notification recommended."
        elif "HIGH" in prompt:
            threat_note = "🔴 **HIGH THREAT ENVIRONMENT**. Elevated operational security posture advised."
        else:
            threat_note = "📊 **STANDARD INTELLIGENCE ASSESSMENT** — threat profile within normal parameters."

        context_note = ""
        if has_context:
            context_note = "\n**Historical Context**: Analysis informed by retrieved incident intelligence from the Sentinel database."
        if has_live:
            context_note += "\n**Live Intelligence**: Real-time feeds incorporated into this assessment."

        response = f"""## SENTINEL Intelligence Briefing
*Generated: {now}*

{threat_note}

**Situation Assessment**

Based on the retrieved intelligence, this region presents a complex threat environment characterized by recurring patterns of conflict. Historical data indicates a persistent operational tempo with multiple documented incidents matching the query profile.

**Key Intelligence Findings**

- Pattern analysis reveals systematic targeting consistent with organized threat actors
- Regional incident density suggests sustained operational capability in the area of interest
- Attack methodology aligns with documented signatures from the intelligence database
- Casualty patterns indicate professional execution with prior operational planning

**Risk Trajectory**

Current intelligence suggests the threat environment is dynamic. Historical precedents in similar regions indicate potential for tactical evolution. Monitoring of logistics networks, communications indicators, and population movement patterns is recommended.

**Strategic Assessment**

The available evidence supports a posture of heightened vigilance. Intelligence gaps exist in source corroboration and real-time confirmation. All assessments should be validated against human intelligence and signals intelligence where available.

**Recommendations**

1. Increase collection frequency for the specified area of operation
2. Cross-reference with allied intelligence services for corroborating assessments  
3. Review existing force protection measures and update threat matrix
4. Schedule follow-up intelligence review in 48-72 hours
{context_note}

---
*Note: This response is generated by Sentinel AI Mock LLM. Configure GEMINI_API_KEY in .env for AI-powered analysis.*"""

        return response
