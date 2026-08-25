"""
API Client — Sentinel AI V2.0
Frontend ↔ Backend communication layer.
All functions return None on failure; pages handle gracefully.
"""
import requests
import streamlit as st
import os

# API_BASE_URL = "http://127.0.0.1:8001/api/v1"
API_BASE_URL = os.getenv("API_BASE_URL", os.getenv("API_URL", "http://127.0.0.1:8001/api/v1"))

def api_post(endpoint: str, payload: dict, timeout: int = 30):
    try:
        response = requests.post(
            f"{API_BASE_URL}/{endpoint}",
            json=payload,
            timeout=timeout
        )
        if response.status_code == 422:
            detail = response.json().get("detail", "Validation error")
            st.error(f"API Validation Error (422): {detail}")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend API is not running. Start the server with: `uvicorn api.main:app --reload`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ API request timed out. The backend may be processing a large query.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_get(endpoint: str, timeout: int = 15):
    try:
        response = requests.get(
            f"{API_BASE_URL}/{endpoint}",
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend API is not running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


# ── Threat Assessment ─────────────────────────────────────────────────────────

def predict_threat(data: dict):
    """
    Full risk assessment payload:
    {attack_type, target_type, weapon_type, region, country, fatalities, injuries, property_damage}
    """
    return api_post("predict/evaluate", data)


# ── Incident Search ───────────────────────────────────────────────────────────

def search_incidents(
    query: str,
    top_k: int = 5,
    country: str = None,
    region: str = None,
    attack_type: str = None,
    year_from: int = None,
    year_to: int = None,
):
    payload = {"query": query, "top_k": top_k}
    if country:
        payload["country"] = country
    if region:
        payload["region"] = region
    if attack_type:
        payload["attack_type"] = attack_type
    if year_from:
        payload["year_from"] = year_from
    if year_to:
        payload["year_to"] = year_to
    return api_post("search/query", payload)


# ── Report Generation ─────────────────────────────────────────────────────────

def generate_report(query: str, risk_assessment: dict = None, top_k: int = 5):
    """
    Generate intelligence report.
    risk_assessment is optional — backend will generate one if not provided.
    """
    payload = {
        "query": query,
        "top_k_incidents": top_k,
    }
    if risk_assessment:
        payload["risk_assessment"] = risk_assessment
    return api_post("report/generate", payload, timeout=60)


# ── Intelligence Copilot ──────────────────────────────────────────────────────

def chat_copilot(query: str, history: list, top_k: int = 5):
    """
    Multi-turn conversational intelligence query.
    history: list of {role: str, content: str}
    """
    return api_post("chat/", {
        "query": query,
        "history": history,
        "top_k_incidents": top_k
    }, timeout=45)


# ── Data & Analytics ──────────────────────────────────────────────────────────

def get_dataset_stats():
    """Fetch high-level dataset statistics for dashboard."""
    return api_get("data/stats")


def get_analytics(chart_type: str, **kwargs):
    """
    Fetch analytics data for a specific chart type.
    chart_types: country_ranking, fatality_trend, attack_distribution,
                 weapon_distribution, target_distribution, regional_comparison,
                 monthly_trend, heatmap_data, incident_timeline
    """
    payload = {"chart_type": chart_type, **kwargs}
    return api_post("data/analytics", payload)
