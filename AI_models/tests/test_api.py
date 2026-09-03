import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test /health endpoint returns HTTP 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "VeriGate" in data["service"]


def test_watchlist_endpoint_hit():
    """Test /watchlist endpoint with demo flagged record."""
    response = client.get("/watchlist?passport_number=X9988776")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["details"]["status"] == "FLAGGED"


def test_screen_endpoint_with_sample_image(tmp_path):
    """Test full /screen endpoint using synthetic sample image."""
    # Read sample image from sample_documents directory
    from app.config import SAMPLE_DOCS_DIR
    sample_pass_path = SAMPLE_DOCS_DIR / "case1_genuine_passport.png"
    sample_face_path = SAMPLE_DOCS_DIR / "case1_genuine_face.png"

    if sample_pass_path.exists() and sample_face_path.exists():
        with open(sample_pass_path, "rb") as pass_f, open(sample_face_path, "rb") as face_f:
            files = {
                "document": ("passport.png", pass_f, "image/png"),
                "verification_photo": ("face.png", face_f, "image/png")
            }
            data = {"document_type": "passport"}
            response = client.post("/screen", files=files, data=data)
            
            assert response.status_code == 200
            res = response.json()
            assert "screening_id" in res
            assert "document" in res
            assert "validation" in res
            assert "tampering" in res
            assert "face_verification" in res
            assert "risk_assessment" in res
