# VeriGate AI 🛡️
### Intelligent Document & Identity Verification Platform (SIH Prototype)

VeriGate AI is a modular, AI-assisted document and identity screening platform designed for border security, passport control, and automated identity verification.

Built for the **Smart India Hackathon (SIH)**, VeriGate AI prioritizes an **end-to-end working MVP**, **modular extensibility**, **explainable risk scoring**, and a **polished dark-mode security UI**.

---

## 🌟 Key Features

1. **Abstract Multi-Document Architecture**: Extensible `BaseDocumentProcessor` interface allowing simple addition of Visas, National IDs, Driving Licenses, and Residence Permits without rewriting core application logic.
2. **Passport OCR & TD3 MRZ Parsing**: Robust extraction of identity fields with ICAO 9303 7-3-1 check digit validation for Passport #, Date of Birth, Expiry Date, and Composite checksum.
3. **Dual Image Forensics & Tampering Engine**: Error Level Analysis (ELA), Noise Variance Analysis, and Edge Discontinuity detection to locate text manipulation, photo replacement, and compression anomalies with Base64 heatmap overlays.
4. **1-to-1 Facial Verification**: Automated face crop extraction and similarity comparison between passport document photo and live verification photo.
5. **Explainable Risk Scoring Engine**: Configurable weighted risk calculation (Tampering 35%, Face 30%, Document Validity 20%, MRZ 10%, Blacklist 5%) outputting actionable recommendations (*Proceed*, *Manual Review*, *Secondary Inspection*).
6. **Synthetic Demo Watchlist & SQLite Audit Trail**: Searchable audit database preserving non-sensitive screening metadata.
7. **1-Click SIH Preset Scenarios**: Pre-generated synthetic test cases for instant live judging demos.

---

## 🏗️ Project Architecture

```text
verigate-ai/
├── app/
│   ├── main.py                  # FastAPI server & REST route orchestration
│   ├── config.py                # System settings & risk weights configuration
│   ├── ocr/
│   │   ├── base_processor.py    # Abstract Base Document Processor Interface
│   │   ├── passport_processor.py# Passport OCR & field extraction implementation
│   │   ├── ocr_module.py        # Processor registry & central dispatcher
│   │   └── mrz.py               # 2-Line TD3 MRZ detector, parser & check digit validator
│   ├── validation/
│   │   └── validation_module.py # Format, logic, date, and OCR↔MRZ consistency checks
│   ├── tampering/
│   │   └── tampering_module.py  # ELA, Noise variance, Edge anomaly & PyTorch model interface
│   ├── face/
│   │   └── face_module.py       # OpenCV Haar Cascade / DeepFace 1-to-1 face crop verification
│   ├── risk/
│   │   └── risk_engine.py       # Explainable weighted risk score & recommendation engine
│   ├── database/
│   │   └── database.py          # SQLite database schema, CRUD operations & demo watchlist
│   └── utils/
│       ├── helpers.py           # Image formatting, Base64 converters & heatmap overlays
│       └── sample_generator.py  # Synthetic passport image & test case generator
├── frontend/
│   └── streamlit_app.py         # Modern dark-mode Streamlit Dashboard & Screening UI
├── data/
│   ├── sample_documents/        # Auto-generated synthetic SIH test case images
│   └── verigate.db              # SQLite database (auto-created)
├── tests/
│   ├── test_mrz.py              # Unit tests for MRZ parsing & checksums
│   ├── test_validation.py       # Unit tests for validation rules & OCR consistency
│   ├── test_tampering.py        # Unit tests for tampering heuristics
│   ├── test_risk.py             # Unit tests for risk calculation
│   └── test_api.py              # Integration tests for FastAPI endpoints
├── requirements.txt             # Free & open-source Python dependencies
├── Dockerfile                   # Unified containerization definition
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: Streamlit, Plotly, Custom CSS
- **Computer Vision & Image Forensics**: OpenCV, Pillow, NumPy
- **Machine Learning & Deep Learning**: PyTorch, scikit-learn
- **Database**: SQLite
- **Testing**: Pytest, HTTPX

*(All technologies used are 100% free and open-source with no paid API dependencies).*

---

## ⚡ Quick Start & Installation

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-org/verigate-ai.git
cd verigate-ai

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Synthetic Test Cases

```bash
python -m app.utils.sample_generator
```

### 4. Run Automated Tests

```bash
python -m pytest tests/ -v
```

---

## 🚀 Running the Application

### Option A: Run FastAPI Backend & Streamlit Separately

**Terminal 1 (FastAPI Backend):**
```bash
uvicorn app.main:app --reload --port 8000
```
*API Swagger Documentation will be available at `http://localhost:8000/docs`.*

**Terminal 2 (Streamlit UI):**
```bash
streamlit run frontend/streamlit_app.py
```
*Web App will be available at `http://localhost:8501`.*

### Option B: Run via Docker

```bash
docker build -t verigate-ai .
docker run -p 8000:8000 -p 8501:8501 verigate-ai
```

---

## 🏆 SIH Judging Demo Walkthrough

1. Open `http://localhost:8501` in your browser.
2. Navigate to **🔍 Live AI Screening**.
3. Under **1. Quick Load Preset SIH Test Cases**, click any of the 4 pre-configured scenario buttons:
   - 🟢 **Case 1: Genuine Passport** → OCR ✓, MRZ Checksums ✓, Forensics Clear ✓, Face Match ✓ → **LOW RISK (Green)**
   - 🟡 **Case 2: Expired Passport** → Expiry Check ✗ → **MEDIUM RISK (Yellow)**
   - 🔴 **Case 3: Tampered Document** → ELA Anomaly ⚠, Text Splicing ⚠ → **HIGH RISK (Red)** + Heatmap Highlight
   - 🔴 **Case 4: Face Mismatch** → Impostor Photo ✗ → **HIGH RISK (Red)** + Identity Mismatch Alert
4. Click **🚀 START AI SCREENING** to watch the multi-layered pipeline execute live!

---

## 🔌 API Endpoints Reference

- `POST /screen` — Orchestrates full screening pipeline (Document + Verification Photo).
- `POST /ocr` — Extracts structured fields and parses MRZ from document image.
- `POST /validate` — Runs rule validation on extracted document JSON.
- `POST /tampering` — Runs Error Level Analysis (ELA) and returns heatmap visualization.
- `POST /face` — Compares document face crop against verification photo.
- `GET /result/{screening_id}` — Retrieves past screening audit report.
- `GET /watchlist?passport_number=X9988776` — Searches synthetic watchlist database.
- `GET /health` — System status and module capabilities.

---

## 🧩 Developer Extensibility Guide

### How to Add a New Document Type (e.g. VisaProcessor)

1. Create `app/ocr/visa_processor.py` inheriting from `BaseDocumentProcessor`:
```python
from app.ocr.base_processor import BaseDocumentProcessor

class VisaProcessor(BaseDocumentProcessor):
    def get_supported_document_type(self) -> str:
        return "visa"

    def process_document(self, image):
        # Implement visa specific OCR extraction
        return {
            "document_type": "visa",
            "name": "...",
            "visa_number": "...",
            "confidence": 0.90
        }
```

2. Register the processor in `app/ocr/ocr_module.py`:
```python
from app.ocr.visa_processor import VisaProcessor
register_processor("visa", VisaProcessor)
```

### How to Replace the Tampering Model

Replace `detect_tampering` inside `app/tampering/tampering_module.py`. As long as your function returns the standard JSON dictionary schema (`tampered`, `confidence`, `tampering_score`, `risk_level`, `visualization_heatmap_b64`), no changes to UI, API, or Risk engine are necessary.

---

## 📜 Disclaimer

> **VeriGate AI is an AI-assisted screening prototype intended to support human decision-making. It does not replace authorized border, immigration, law-enforcement, or government decision-making.**
> All sample documents, passport numbers, names, and watchlist records included in this repository are synthetic demo data generated strictly for evaluation purposes.
