import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import config
from app.utils.helpers import bytes_to_cv2
from app.ocr.ocr_module import extract_document
from app.validation.validation_module import validate_document
from app.tampering.tampering_module import detect_tampering
from app.face.face_module import verify_face
from app.risk.risk_engine import calculate_risk
from app.database.database import (
    init_db, save_screening, get_screening_by_id, get_recent_screenings, search_watchlist, get_screening_stats
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed demo data on startup."""
    init_db()
    yield

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description="Intelligent Document & Identity Verification Platform (SIH Prototype)",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import RedirectResponse

@app.get("/")
def root_redirect():
    """Redirect root GET / to interactive OpenAPI documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    """System health check and loaded module capabilities."""
    return {
        "status": "healthy",
        "service": config.PROJECT_NAME,
        "version": config.VERSION,
        "supported_documents": ["passport", "visa (extensible)", "national_id (extensible)"],
        "modules": {
            "ocr": "Active (Passport OCR + TD3 MRZ Parser)",
            "mrz": "Active (7-3-1 Checksum Validation)",
            "validation": "Active (Rule-based + Synthetic Watchlist)",
            "tampering": "Active (Error Level Analysis + Noise Variance)",
            "face_verification": "Active (1-to-1 Facial Crop Match)"
        },
        "disclaimer": "VeriGate AI is an AI-assisted screening prototype."
    }


@app.post("/screen")
async def screen_document(
    document: UploadFile = File(...),
    verification_photo: Optional[UploadFile] = File(None),
    document_type: str = Form("passport")
):
    """
    Main Screening Endpoint.
    Orchestrates OCR -> MRZ -> Validation -> Tampering -> Face -> Risk -> SQLite Audit.
    """
    try:
        doc_bytes = await document.read()
        doc_cv2 = bytes_to_cv2(doc_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid passport document image file: {str(e)}")

    ver_cv2 = None
    if verification_photo:
        try:
            ver_bytes = await verification_photo.read()
            ver_cv2 = bytes_to_cv2(ver_bytes)
        except Exception:
            ver_cv2 = None

    screening_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    # 1. OCR & MRZ Extraction
    ocr_result = extract_document(doc_cv2, document_type=document_type)

    # 2. Document Validation & Watchlist lookup
    val_result = validate_document(ocr_result)

    # 3. Image Forensics & Tampering Analysis
    tampering_result = detect_tampering(doc_cv2)

    # 4. Face Verification (if verification photo provided)
    if ver_cv2 is not None:
        face_result = verify_face(doc_cv2, ver_cv2)
    else:
        face_result = {
            "face_detected": False,
            "document_face_detected": False,
            "verification_face_detected": False,
            "similarity": 0.0,
            "match": False,
            "confidence": 0.0,
            "document_face_b64": "",
            "verification_face_b64": "",
            "message": "No verification photograph was uploaded for 1-to-1 face comparison."
        }

    # 5. Explainable Risk Scoring Engine
    risk_result = calculate_risk(ocr_result, val_result, tampering_result, face_result)

    # 6. Build Final Combined Report
    full_report = {
        "screening_id": screening_id,
        "timestamp": timestamp,
        "document": ocr_result,
        "validation": val_result,
        "tampering": tampering_result,
        "face_verification": face_result,
        "risk_assessment": risk_result,
        "disclaimer": "VeriGate AI is an AI-assisted screening prototype intended to support human verification."
    }

    # 7. Persist in SQLite Audit Database
    save_screening(full_report)

    return full_report


@app.post("/ocr")
async def ocr_endpoint(
    document: UploadFile = File(...),
    document_type: str = Form("passport")
):
    """Granular OCR & MRZ extraction endpoint."""
    doc_bytes = await document.read()
    doc_cv2 = bytes_to_cv2(doc_bytes)
    return extract_document(doc_cv2, document_type=document_type)


@app.post("/validate")
def validate_endpoint(ocr_data: Dict[str, Any]):
    """Granular document validation endpoint."""
    return validate_document(ocr_data)


@app.post("/tampering")
async def tampering_endpoint(document: UploadFile = File(...)):
    """Granular tampering detection endpoint."""
    doc_bytes = await document.read()
    doc_cv2 = bytes_to_cv2(doc_bytes)
    return detect_tampering(doc_cv2)


@app.post("/face")
async def face_endpoint(
    document: UploadFile = File(...),
    verification_photo: UploadFile = File(...)
):
    """Granular 1-to-1 face verification endpoint."""
    doc_bytes = await document.read()
    ver_bytes = await verification_photo.read()
    return verify_face(bytes_to_cv2(doc_bytes), bytes_to_cv2(ver_bytes))


@app.get("/result/{screening_id}")
def get_result(screening_id: str):
    """Retrieve past screening audit record by ID."""
    result = get_screening_by_id(screening_id)
    if not result:
        raise HTTPException(status_code=404, detail="Screening ID not found")
    return result


@app.get("/recent")
def get_recent(limit: int = Query(20, ge=1, le=100)):
    """Get list of recent screenings for dashboard."""
    return get_recent_screenings(limit)


@app.get("/stats")
def get_stats():
    """Get dashboard summary statistics."""
    return get_screening_stats()


@app.get("/watchlist")
def query_watchlist(passport_number: str):
    """Query synthetic watchlist database."""
    res = search_watchlist(passport_number)
    if not res:
        return {"found": False, "message": "No match in demo watchlist"}
    return {"found": True, "details": res, "disclaimer": "DEMO DATA — NOT A GOVERNMENT DATABASE"}
