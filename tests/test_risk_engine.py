import pytest
from services.risk_engine import RiskEngine

def test_risk_engine_escalation():
    engine = RiskEngine()
    
    # Mocking predictor inside RiskEngine for unit testing
    class MockPredictor:
        def predict(self, data):
            return {
                "threat_level": "MEDIUM",
                "confidence": 0.8,
                "feature_importance": {}
            }
            
    engine.predictor = MockPredictor()
    
    dummy_data = {"fatalities": 0}
    
    # Test Baseline
    result = engine.evaluate_risk(dummy_data, historical_frequency=2)
    assert result['risk_level'] == "ELEVATED"
    
    # Test Frequency Escalation
    result_high_freq = engine.evaluate_risk(dummy_data, historical_frequency=10)
    assert result_high_freq['risk_level'] == "HIGH"
    
    # Test Fatality Escalation
    dummy_data_fatal = {"fatalities": 15}
    result_fatal = engine.evaluate_risk(dummy_data_fatal, historical_frequency=2)
    assert result_fatal['risk_level'] == "HIGH"
