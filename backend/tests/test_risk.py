import pytest
from app.risk.risk_engine import calculate_risk


def test_calculate_risk_low():
    """Test risk calculation for a genuine, fully valid document."""
    ocr_result = {"mrz": {"mrz_detected": True, "overall_mrz_valid": True}}
    val_result = {"is_valid": True, "reasons": [], "watchlist_match": False}
    tamp_result = {"tampered": False, "tampering_score": 10.0, "risk_level": "LOW"}
    face_result = {"match": True, "similarity": 92.5}

    risk = calculate_risk(ocr_result, val_result, tamp_result, face_result)
    
    assert risk["level"] == "LOW"
    assert risk["score"] <= 30
    assert "Proceed to normal verification." in risk["recommendation"]


def test_calculate_risk_high_tampered_wrongface():
    """Test risk calculation when tampering and face mismatch occur."""
    ocr_result = {"mrz": {"mrz_detected": True, "overall_mrz_valid": False}}
    val_result = {"is_valid": False, "reasons": ["Passport number format invalid"], "watchlist_match": False}
    tamp_result = {"tampered": True, "tampering_score": 85.0, "risk_level": "HIGH"}
    face_result = {"match": False, "similarity": 12.0}

    risk = calculate_risk(ocr_result, val_result, tamp_result, face_result)
    
    assert risk["level"] == "HIGH"
    assert risk["score"] > 60
    assert "Secondary inspection recommended." in risk["recommendation"]
    assert len(risk["reasons"]) >= 2
