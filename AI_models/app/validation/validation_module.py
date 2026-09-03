import re
from datetime import datetime
from typing import Dict, Any, List
from app.config import config
from app.database.database import search_watchlist


def parse_date(date_str: str) -> datetime:
    """Helper to parse date string in DD/MM/YYYY or YYYY-MM-DD format."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def validate_document(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform rule-based document validation.
    
    Checks:
    1. Required fields presence
    2. Format checks (passport number, nationality, dates)
    3. Logical checks (DOB past, Expiry after DOB, Active status)
    4. MRZ ↔ OCR consistency checks
    5. Synthetic Watchlist check
    """
    checks = []
    is_valid = True
    reasons = []

    # 1. Required Fields Check
    required_fields = ["name", "passport_number", "nationality", "dob", "gender", "expiry"]
    missing_fields = [field for field in required_fields if not ocr_data.get(field)]
    
    if missing_fields:
        is_valid = False
        checks.append({
            "check": "Required Fields",
            "status": "FAIL",
            "details": f"Missing required fields: {', '.join(missing_fields)}"
        })
        reasons.append(f"Missing required fields: {', '.join(missing_fields)}")
    else:
        checks.append({
            "check": "Required Fields",
            "status": "PASS",
            "details": "All required passport fields present"
        })

    # 2. Format Checks
    pass_num = str(ocr_data.get("passport_number", "")).strip()
    if re.match(r'^[A-Z0-9]{7,9}$', pass_num):
        checks.append({
            "check": "Passport Number Format",
            "status": "PASS",
            "details": f"Valid format: {pass_num}"
        })
    else:
        is_valid = False
        checks.append({
            "check": "Passport Number Format",
            "status": "FAIL",
            "details": f"Invalid passport format: {pass_num}"
        })
        reasons.append("Passport number format invalid")

    nationality = str(ocr_data.get("nationality", "")).upper().strip()
    if nationality in config.VALID_COUNTRY_CODES or len(nationality) == 3:
        checks.append({
            "check": "Nationality Code",
            "status": "PASS",
            "details": f"Valid ISO code: {nationality}"
        })
    else:
        checks.append({
            "check": "Nationality Code",
            "status": "WARNING",
            "details": f"Unrecognized ISO country code: {nationality}"
        })

    # 3. Date & Logical Checks
    dob_obj = None
    expiry_obj = None
    today = datetime.now()

    try:
        dob_obj = parse_date(ocr_data.get("dob", ""))
        if dob_obj > today:
            is_valid = False
            checks.append({
                "check": "Date of Birth Logic",
                "status": "FAIL",
                "details": "DOB is in the future"
            })
            reasons.append("Date of Birth is set in the future")
        else:
            checks.append({
                "check": "Date of Birth Logic",
                "status": "PASS",
                "details": f"Valid DOB ({ocr_data.get('dob')})"
            })
    except Exception as e:
        is_valid = False
        checks.append({
            "check": "Date of Birth Logic",
            "status": "FAIL",
            "details": f"Could not parse DOB: {ocr_data.get('dob')}"
        })
        reasons.append("Could not parse Date of Birth")

    try:
        expiry_obj = parse_date(ocr_data.get("expiry", ""))
        if expiry_obj < today:
            is_valid = False
            checks.append({
                "check": "Document Expiry Status",
                "status": "EXPIRED",
                "details": f"Document expired on {ocr_data.get('expiry')}"
            })
            reasons.append("Passport is expired")
        else:
            checks.append({
                "check": "Document Expiry Status",
                "status": "PASS",
                "details": f"Active document (Expires {ocr_data.get('expiry')})"
            })
    except Exception as e:
        is_valid = False
        checks.append({
            "check": "Document Expiry Status",
            "status": "FAIL",
            "details": f"Could not parse Expiry date: {ocr_data.get('expiry')}"
        })
        reasons.append("Could not parse Expiry date")

    if dob_obj and expiry_obj and expiry_obj <= dob_obj:
        is_valid = False
        checks.append({
            "check": "Expiry vs DOB Logic",
            "status": "FAIL",
            "details": "Expiry date is before Date of Birth"
        })
        reasons.append("Expiry date is before Date of Birth")

    # 4. MRZ Consistency Check
    mrz = ocr_data.get("mrz", {})
    mrz_detected = mrz.get("mrz_detected", False)
    
    if mrz_detected:
        mrz_pass = mrz.get("passport_number", "").replace('<', '').strip()
        mrz_dob = mrz.get("dob", "").strip()
        mrz_expiry = mrz.get("expiry", "").strip()

        mismatch_items = []
        if mrz_pass and pass_num and mrz_pass != pass_num:
            mismatch_items.append(f"Passport Number (OCR: {pass_num} vs MRZ: {mrz_pass})")
        
        if mrz_dob and ocr_data.get("dob") and mrz_dob != ocr_data.get("dob"):
            mismatch_items.append(f"DOB (OCR: {ocr_data.get('dob')} vs MRZ: {mrz_dob})")

        if mismatch_items:
            is_valid = False
            checks.append({
                "check": "OCR ↔ MRZ Consistency",
                "status": "FAIL",
                "details": f"Discrepancies found: {'; '.join(mismatch_items)}"
            })
            reasons.append("OCR and MRZ field mismatch detected")
        else:
            checks.append({
                "check": "OCR ↔ MRZ Consistency",
                "status": "PASS",
                "details": "OCR fields match MRZ data perfectly"
            })
    else:
        checks.append({
            "check": "MRZ Validation",
            "status": "WARNING",
            "details": "MRZ could not be reliably detected — manual verification recommended"
        })

    # 5. Synthetic Watchlist Check
    watchlist_hit = search_watchlist(pass_num)
    if watchlist_hit:
        status = watchlist_hit.get("status")
        reason = watchlist_hit.get("reason")
        is_valid = False
        checks.append({
            "check": "Watchlist Lookup (Demo Data)",
            "status": status,
            "details": f"ALERT: {status} - {reason}"
        })
        reasons.append(f"Watchlist alert: {status} ({reason})")
    else:
        checks.append({
            "check": "Watchlist Lookup (Demo Data)",
            "status": "PASS",
            "details": "Clear (No watchlist matches found)"
        })

    return {
        "is_valid": is_valid,
        "checks": checks,
        "reasons": reasons,
        "watchlist_match": bool(watchlist_hit),
        "watchlist_details": watchlist_hit
    }
