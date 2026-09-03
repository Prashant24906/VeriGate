from typing import Dict, Any, List
from app.config import config


def calculate_risk(
    ocr_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    tampering_result: Dict[str, Any],
    face_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Explainable Risk Engine.
    Combines weighted risk factors across all screening components.
    
    Weights:
    - Tampering (35%)
    - Face Verification (30%)
    - Document Validity (20%)
    - MRZ Validation (10%)
    - Blacklist / Expiry (5%)
    
    Risk Bands:
    0–30   : LOW
    31–60  : MEDIUM
    61–100 : HIGH
    """
    w = config.WEIGHTS
    reasons = []

    # 1. Tampering Component (Weight 35%)
    tamper_score = tampering_result.get("tampering_score", 0.0)
    is_tampered = tampering_result.get("tampered", False)
    if is_tampered:
        tamper_risk_contrib = max(70.0, tamper_score)
        reasons.append(f"Potential document tampering detected ({tampering_result.get('risk_level', 'HIGH')} risk)")
    else:
        tamper_risk_contrib = min(30.0, tamper_score)

    # 2. Face Verification Component (Weight 30%)
    face_match = face_result.get("match", False)
    face_similarity = face_result.get("similarity", 0.0)
    if not face_match:
        face_risk_contrib = max(80.0, 100.0 - face_similarity)
        reasons.append(f"Face verification failed (Similarity: {face_similarity}%)")
    else:
        face_risk_contrib = max(0.0, 100.0 - face_similarity)

    # 3. Document Validity Component (Weight 20%)
    doc_valid = validation_result.get("is_valid", False)
    val_reasons = validation_result.get("reasons", [])
    if not doc_valid:
        doc_risk_contrib = 85.0
        for r in val_reasons:
            if r not in reasons:
                reasons.append(r)
    else:
        doc_risk_contrib = 5.0

    # 4. MRZ Validation Component (Weight 10%)
    mrz = ocr_result.get("mrz", {})
    mrz_valid = mrz.get("overall_mrz_valid", False)
    mrz_detected = mrz.get("mrz_detected", False)
    if not mrz_detected:
        mrz_risk_contrib = 60.0
        reasons.append("MRZ could not be reliably detected — manual verification recommended")
    elif not mrz_valid:
        mrz_risk_contrib = 80.0
        reasons.append("MRZ checksum validation failed")
    else:
        mrz_risk_contrib = 0.0

    # 5. Blacklist / Expiry Component (Weight 5%)
    watchlist_hit = validation_result.get("watchlist_match", False)
    if watchlist_hit:
        wl_risk_contrib = 100.0
        wl_details = validation_result.get("watchlist_details", {})
        reasons.append(f"Watchlist Hit: {wl_details.get('status')} ({wl_details.get('reason')})")
    else:
        wl_risk_contrib = 0.0

    # Calculate final weighted risk score
    total_score = (
        (tamper_risk_contrib * w.tampering) +
        (face_risk_contrib * w.face_verification) +
        (doc_risk_contrib * w.document_validity) +
        (mrz_risk_contrib * w.mrz_validation) +
        (wl_risk_contrib * w.blacklist_expiry)
    )

    final_score = int(round(total_score))
    final_score = max(0, min(100, final_score))

    # Determine risk level and recommendation
    if final_score <= config.THRESHOLDS.low_max:
        level = "LOW"
        recommendation = "Proceed to normal verification."
    elif final_score <= config.THRESHOLDS.medium_max:
        level = "MEDIUM"
        recommendation = "Manual review recommended."
    else:
        level = "HIGH"
        recommendation = "Secondary inspection recommended."

    if not reasons and level == "LOW":
        reasons.append("All automated identity checks passed successfully.")

    return {
        "score": final_score,
        "level": level,
        "recommendation": recommendation,
        "reasons": reasons,
        "weights_applied": {
            "tampering": w.tampering,
            "face_verification": w.face_verification,
            "document_validity": w.document_validity,
            "mrz_validation": w.mrz_validation,
            "blacklist_expiry": w.blacklist_expiry
        },
        "component_risk_scores": {
            "tampering": round(tamper_risk_contrib, 1),
            "face_verification": round(face_risk_contrib, 1),
            "document_validity": round(doc_risk_contrib, 1),
            "mrz_validation": round(mrz_risk_contrib, 1),
            "blacklist_expiry": round(wl_risk_contrib, 1)
        },
        "disclaimer": "VeriGate AI is an AI-assisted screening prototype intended to support human decision-making."
    }
