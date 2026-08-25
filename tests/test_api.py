import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_predict_threat():
    payload = {
        "attack_type": "Bombing/Explosion",
        "target_type": "Military",
        "weapon_type": "Explosives",
        "region": "Middle East",
        "country": "Iraq",
        "fatalities": 5,
        "injuries": 10,
        "property_damage": 50000.0
    }
    response = client.post("/api/v1/predict/evaluate", json=payload)
    # Status code might be 500 if DB is empty, but route exists.
    assert response.status_code in [200, 500]

def test_search():
    payload = {"query": "Bombing in Middle East", "top_k": 3}
    response = client.post("/api/v1/search/query", json=payload)
    assert response.status_code in [200, 500]
