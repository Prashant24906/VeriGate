import pytest
from app.validation.validation_module import validate_document


def test_validate_document_valid():
    """Test validation on a perfectly valid passport data dict."""
    ocr_data = {
        "document_type": "passport",
        "name": "JOHN DOE",
        "passport_number": "A1234567",
        "nationality": "IND",
        "dob": "15/08/1999",
        "gender": "M",
        "expiry": "15/08/2030",
        "mrz": {
            "mrz_detected": True,
            "passport_number": "A1234567",
            "dob": "15/08/1999",
            "expiry": "15/08/2030",
            "overall_mrz_valid": True
        }
    }

    result = validate_document(ocr_data)
    assert result["is_valid"] is True
    assert result["watchlist_match"] is False


def test_validate_document_expired():
    """Test validation on an expired passport."""
    ocr_data = {
        "document_type": "passport",
        "name": "ALICE SMITH",
        "passport_number": "Z1122334",
        "nationality": "IND",
        "dob": "10/10/1985",
        "gender": "F",
        "expiry": "01/01/2020",
        "mrz": {
            "mrz_detected": True,
            "passport_number": "Z1122334",
            "dob": "10/10/1985",
            "expiry": "01/01/2020",
            "overall_mrz_valid": True
        }
    }

    result = validate_document(ocr_data)
    assert result["is_valid"] is False
    assert any("expired" in r.lower() for r in result["reasons"])


def test_validate_document_mrz_mismatch():
    """Test validation when OCR passport number mismatches MRZ."""
    ocr_data = {
        "document_type": "passport",
        "name": "JOHN DOE",
        "passport_number": "FORGED999",
        "nationality": "IND",
        "dob": "15/08/1999",
        "gender": "M",
        "expiry": "15/08/2030",
        "mrz": {
            "mrz_detected": True,
            "passport_number": "A1234567",  # Mismatch
            "dob": "15/08/1999",
            "expiry": "15/08/2030",
            "overall_mrz_valid": True
        }
    }

    result = validate_document(ocr_data)
    assert result["is_valid"] is False
    assert any("mismatch" in r.lower() for r in result["reasons"])
