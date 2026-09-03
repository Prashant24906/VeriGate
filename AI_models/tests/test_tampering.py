import pytest
import numpy as np
import cv2
from app.tampering.tampering_module import detect_tampering, compute_ela


def test_tampering_detection_structure():
    """Test returned schema and fields from tampering detection engine."""
    # Create a synthetic 400x300 image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 200
    cv2.putText(img, "TEST PASSPORT", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    
    result = detect_tampering(img)
    
    assert "tampered" in result
    assert "confidence" in result
    assert "tampering_score" in result
    assert "risk_level" in result
    assert "analysis_mode" in result
    assert "visualization_heatmap_b64" in result
    assert result["visualization_heatmap_b64"].startswith("data:image/png;base64,")


def test_ela_computation():
    """Test Error Level Analysis computation returns grayscale diff array."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 240
    ela_mask, ela_score = compute_ela(img)
    
    assert ela_mask.shape == (200, 200)
    assert isinstance(ela_score, float)
