import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Check if running in Vercel Serverless environment (/tmp is the only writable directory)
IS_VERCEL = "VERCEL" in os.environ or os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    DATA_DIR = Path("/tmp/data")
    SAMPLE_DOCS_DIR = DATA_DIR / "sample_documents"
    DB_PATH = Path("/tmp/verigate.db")
else:
    DATA_DIR = BASE_DIR / "data"
    SAMPLE_DOCS_DIR = DATA_DIR / "sample_documents"
    DB_PATH = DATA_DIR / "verigate.db"

# Ensure directories exist
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


class RiskWeights(BaseModel):
    tampering: float = 0.35
    face_verification: float = 0.30
    document_validity: float = 0.20
    mrz_validation: float = 0.10
    blacklist_expiry: float = 0.05


class RiskThresholds(BaseModel):
    low_max: int = 30
    medium_max: int = 60
    # >60 is HIGH


class Config:
    PROJECT_NAME: str = "VeriGate AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Risk weights
    WEIGHTS: RiskWeights = RiskWeights()
    THRESHOLDS: RiskThresholds = RiskThresholds()
    
    # DB
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    # Face verification threshold
    FACE_MATCH_THRESHOLD: float = 0.60  # Cosine similarity > 0.60 considered match

    # Valid Country Codes (ISO 3166-1 alpha-3 subset for validation)
    VALID_COUNTRY_CODES: set = {
        "IND", "USA", "GBR", "CAN", "AUS", "DEU", "FRA", "JPN", "CHN", "SGP",
        "ARE", "BRA", "ZAF", "ITA", "ESP", "NLD", "CHE", "RUS", "MEX", "KOR"
    }


config = Config()
