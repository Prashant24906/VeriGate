import sys
import os

# Ensure project root directory is in sys.path for app module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import time
import base64
import requests
import pandas as pd
import numpy as np
import cv2
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Import local backend modules for direct in-process execution option or API calls
from app.config import config, SAMPLE_DOCS_DIR
from app.utils.helpers import bytes_to_cv2, cv2_to_base64
from app.ocr.ocr_module import extract_document
from app.validation.validation_module import validate_document
from app.tampering.tampering_module import detect_tampering
from app.face.face_module import verify_face
from app.risk.risk_engine import calculate_risk
from app.database.database import (
    init_db, save_screening, get_screening_by_id, get_recent_screenings, search_watchlist, get_screening_stats
)

# Initialize Streamlit Page Config
st.set_page_config(
    page_title="VeriGate AI — Intelligent Document & Identity Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Security Dark Theme & Niko Robot Styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1E2640 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    /* Title styling */
    .app-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .app-subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Metric Cards */
    .metric-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Risk Badges */
    .badge-low {
        background-color: #064E3B;
        color: #34D399;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-medium {
        background-color: #78350F;
        color: #FBBF24;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-high {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    /* Pipeline Step Box */
    .pipeline-step {
        background-color: #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 10px 16px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Niko Robot Styling */
    .niko-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        border: 2px solid #818CF8;
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 16px;
        box-shadow: 0 0 20px rgba(129, 140, 248, 0.35);
    }
    .niko-header {
        font-size: 1.15rem;
        font-weight: 800;
        color: #A5B4FC;
        margin-bottom: 6px;
    }
    .niko-sub {
        font-size: 0.85rem;
        color: #CBD5E1;
    }
    
    /* Disclaimer Box */
    .disclaimer-box {
        background-color: #0F172A;
        border: 1px dashed #475569;
        border-radius: 8px;
        padding: 12px;
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()

# Pop-up Welcome Toast for Niko Robot Assistant
if "niko_welcome_shown" not in st.session_state:
    st.toast("🤖 Beep Boop! I'm Niko, your AI Screening Assistant! Need help running SIH test cases? Chat with me in the sidebar!", icon="🤖")
    st.session_state.niko_welcome_shown = True

# Niko Chatbot Logic Engine
def get_niko_response(user_query: str) -> str:
    query = user_query.lower().strip()
    
    if any(k in query for k in ["test", "case", "run", "how to test", "demo", "sih", "scenario", "show"]):
        return """🤖 **BEEP BOOP! I am Niko, your VeriGate AI Guide!** Here are the 4 pre-loaded end-to-end test cases you can run right now:

1️⃣ **Case 1: Genuine Passport**
   • *What to expect:* Clean OCR, valid MRZ 7-3-1 check digits, authentic ELA image forensics, and 1-to-1 face match.
   • *Result:* **0–30 LOW RISK (Green)** → "Proceed to normal verification."

2️⃣ **Case 2: Expired Passport**
   • *What to expect:* Clean OCR, but date logic detects an expired document.
   • *Result:* **31–60 MEDIUM RISK (Yellow)** → "Manual review recommended."

3️⃣ **Case 3: Tampered Document**
   • *What to expect:* Spliced text and compression anomalies detected by our Error Level Analysis (ELA) engine.
   • *Result:* **61–100 HIGH RISK (Red)** + Heatmap Overlay showing suspicious text bounding boxes.

4️⃣ **Case 4: Face Mismatch**
   • *What to expect:* Valid document, but live verification photo does NOT match the passport photo.
   • *Result:* **61–100 HIGH RISK (Red)** + ⚠️ "Identity Mismatch Alert".

👉 **Try it now!** Click any of the 4 **Preset SIH Test Case buttons** at the top of the *Live AI Screening* page and hit **🚀 START AI SCREENING**!"""

    elif any(k in query for k in ["tamper", "ela", "forensic", "heat", "fake", "forge"]):
        return """🤖 **BEEP BOOP! Here is how our Image Forensics & Tampering Engine works:**

• **Error Level Analysis (ELA)**: Resaves the passport image at 95% JPEG quality and measures absolute pixel difference matrix to detect text insertion, photo replacement, and image manipulation.
• **Noise Variance & Sharpness**: Analyzes high-frequency noise variance across photo, text, and background zones.
• **Heatmap Overlay**: Suspicious edit regions are surrounded by red bounding boxes and rendered on a Jet colormap heatmap overlay.
• **Analysis Label**: Clearly distinguishes between *AI Model Analysis* and *Prototype Heuristic Analysis* for complete demo honesty!"""

    elif any(k in query for k in ["mrz", "checksum", "icao", "td3", "check digit"]):
        return """🤖 **BEEP BOOP! Here is how MRZ Checksum Validation works:**

• **TD3 Standard**: 2 lines of 44 characters at the bottom of passports.
• **7-3-1 Weighting Algorithm**: Validates check digits for:
  1. Passport Number Checksum
  2. Date of Birth Checksum (YYMMDD)
  3. Expiry Checksum (YYMMDD)
  4. Composite Checksum
• **OCR ↔ MRZ Cross-Check**: Compares visual text fields against MRZ text to catch discrepancies instantly!"""

    elif any(k in query for k in ["face", "photo", "match", "similarity"]):
        return """🤖 **BEEP BOOP! Here is how 1-to-1 Face Verification works:**

• **Face Extraction**: Crops the face from the passport photo and compares it with the live verification photo using OpenCV Haar Cascades / DeepFace.
• **Similarity Threshold**: Computes facial similarity percentage (default threshold > 60.0%).
• **Alerts**: Flags ⚠️ *Identity Mismatch Alert* when verification photo does not match the passport holder."""

    elif any(k in query for k in ["risk", "score", "weight", "explain"]):
        return """🤖 **BEEP BOOP! Here is how our Explainable Risk Engine calculates scores:**

Weighted Formula:
• **Document Tampering**: 35%
• **Face Verification**: 30%
• **Document Validity**: 20%
• **MRZ Validation**: 10%
• **Watchlist Lookup**: 5%

Risk Bands:
• **0–30: LOW RISK** ("Proceed to normal verification")
• **31–60: MEDIUM RISK** ("Manual review recommended")
• **61–100: HIGH RISK** ("Secondary inspection recommended")"""

    else:
        return f"""🤖 **BEEP BOOP! I'm Niko, your AI Screening Assistant!** 

You asked: *"{user_query}"*

Here is what you can explore in VeriGate AI:
• Click **🟢 Case 1: Genuine Passport** for a clean pass.
• Click **🟡 Case 2: Expired Passport** for an expiry warning.
• Click **🔴 Case 3: Tampered Document** to see ELA heatmaps.
• Click **🔴 Case 4: Face Mismatch** to test facial verification.

Need specific help? Click any of the quick prompt buttons below!"""

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/100/security-pass.png", width=70)
st.sidebar.title("VeriGate AI")
st.sidebar.caption("Intelligent Identity Screening Platform")

page = st.sidebar.radio(
    "Navigation Menu",
    ["📊 Dashboard", "🔍 Live AI Screening", "📜 Screening Audit Trail", "🚨 Watchlist Search"],
    index=1
)

st.sidebar.markdown("---")

# ==========================================
# NIKO ROBOT CHATBOT SIDEBAR WIDGET
# ==========================================
st.sidebar.markdown("""
<div class="niko-box">
    <div class="niko-header">🤖 NIKO AI CORE</div>
    <div class="niko-sub">Interactive Screening Guide & Assistant</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("💬 Chat with Niko AI", expanded=True):
    if "niko_chat_history" not in st.session_state:
        st.session_state.niko_chat_history = [
            {"role": "assistant", "content": "🤖 **Beep Boop! I'm Niko!** Ask me what test cases you can run, or click a button below for a guided tour!"}
        ]

    # Display Chat History
    for msg in st.session_state.niko_chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # Quick Suggestion Chips
    st.markdown("**Quick Prompts:**")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        if st.button("🧪 Test Cases", key="btn_q1", use_container_width=True):
            st.session_state.niko_chat_history.append({"role": "user", "content": "What test cases can I run?"})
            st.session_state.niko_chat_history.append({"role": "assistant", "content": get_niko_response("test cases")})
            st.rerun()
    with q_col2:
        if st.button("🔬 Tampering", key="btn_q2", use_container_width=True):
            st.session_state.niko_chat_history.append({"role": "user", "content": "How does Tampering work?"})
            st.session_state.niko_chat_history.append({"role": "assistant", "content": get_niko_response("tamper")})
            st.rerun()

    q_col3, q_col4 = st.columns(2)
    with q_col3:
        if st.button("👤 Face Match", key="btn_q3", use_container_width=True):
            st.session_state.niko_chat_history.append({"role": "user", "content": "How does Face Match work?"})
            st.session_state.niko_chat_history.append({"role": "assistant", "content": get_niko_response("face")})
            st.rerun()
    with q_col4:
        if st.button("⚖️ Risk Score", key="btn_q4", use_container_width=True):
            st.session_state.niko_chat_history.append({"role": "user", "content": "How is Risk calculated?"})
            st.session_state.niko_chat_history.append({"role": "assistant", "content": get_niko_response("risk")})
            st.rerun()

    # Chat Input
    if niko_prompt := st.chat_input("Ask Niko a question...", key="niko_chat_input"):
        st.session_state.niko_chat_history.append({"role": "user", "content": niko_prompt})
        niko_ans = get_niko_response(niko_prompt)
        st.session_state.niko_chat_history.append({"role": "assistant", "content": niko_ans})
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("VeriGate AI MVP v1.0.0 — SIH 2026")


# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
if page == "📊 Dashboard":
    st.markdown("""
    <div class="header-card">
        <div class="app-title">VeriGate AI Dashboard</div>
        <div class="app-subtitle">Real-time Analytics & Operational Screening Overview (DEMO DATA)</div>
    </div>
    """, unsafe_allow_html=True)

    stats = get_screening_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #38BDF8;">{stats['total']}</div>
            <div class="metric-label">Total Screenings</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #34D399;">{stats['low_risk']}</div>
            <div class="metric-label">Low Risk (Proceed)</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #FBBF24;">{stats['medium_risk']}</div>
            <div class="metric-label">Medium Risk (Review)</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #F87171;">{stats['high_risk']}</div>
            <div class="metric-label">High Risk (Inspect)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Risk Distribution")
        if stats['total'] > 0:
            df_pie = pd.DataFrame({
                'Risk Level': ['LOW', 'MEDIUM', 'HIGH'],
                'Count': [stats['low_risk'], stats['medium_risk'], stats['high_risk']]
            })
            fig_pie = px.pie(
                df_pie, values='Count', names='Risk Level',
                color='Risk Level',
                color_discrete_map={'LOW': '#34D399', 'MEDIUM': '#FBBF24', 'HIGH': '#F87171'},
                hole=0.45
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E2E8F0')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No screenings recorded yet. Perform a screening in the Live AI Screening tab.")

    with col2:
        st.subheader("Recent Screening Activity")
        recent_data = get_recent_screenings(limit=10)
        if recent_data:
            df_recent = pd.DataFrame(recent_data)
            st.dataframe(
                df_recent[['timestamp', 'passport_number', 'holder_name', 'validation_status', 'risk_score', 'risk_level']],
                use_container_width=True,
                height=320
            )
        else:
            st.info("No activity logged yet.")


# ==========================================
# PAGE 2: LIVE AI SCREENING
# ==========================================
elif page == "🔍 Live AI Screening":
    st.markdown("""
    <div class="header-card">
        <div class="app-title">VeriGate AI Screening</div>
        <div class="app-subtitle">Multi-layered Document OCR, MRZ Validation, Forensics & Face Verification</div>
    </div>
    """, unsafe_allow_html=True)

    # NIKO BANNER PROMPT ON SCREENING PAGE
    st.info("🤖 **Niko AI Assistant Tip:** Not sure which test cases to run? Click **🧪 Test Cases** in the sidebar or ask Niko in the chatbot to get a full guided tour!")

    # Preset Test Case Buttons for SIH Judging
    st.subheader("1. Quick Load Preset SIH Test Cases")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    
    chosen_preset = None
    with preset_col1:
        if st.button("🟢 Case 1: Genuine Passport", use_container_width=True):
            chosen_preset = "case1"
    with preset_col2:
        if st.button("🟡 Case 2: Expired Passport", use_container_width=True):
            chosen_preset = "case2"
    with preset_col3:
        if st.button("🔴 Case 3: Tampered Document", use_container_width=True):
            chosen_preset = "case3"
    with preset_col4:
        if st.button("🔴 Case 4: Face Mismatch", use_container_width=True):
            chosen_preset = "case4"

    # Setup Session State for Images
    if "passport_img_bytes" not in st.session_state:
        st.session_state.passport_img_bytes = None
    if "verification_img_bytes" not in st.session_state:
        st.session_state.verification_img_bytes = None

    # Handle preset clicks
    if chosen_preset:
        p_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_genuine_passport.png"
        if not p_path.exists():
            p_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_expired_passport.png"
        if not p_path.exists():
            p_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_tampered_passport.png"
        if not p_path.exists():
            p_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_wrongperson_passport.png"

        f_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_genuine_face.png"
        if not f_path.exists():
            f_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_expired_face.png"
        if not f_path.exists():
            f_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_tampered_face.png"
        if not f_path.exists():
            f_path = SAMPLE_DOCS_DIR / f"{chosen_preset}_wrongperson_face.png"

        if p_path.exists() and f_path.exists():
            with open(p_path, "rb") as f1, open(f_path, "rb") as f2:
                st.session_state.passport_img_bytes = f1.read()
                st.session_state.verification_img_bytes = f2.read()
            st.success(f"Loaded Preset {chosen_preset.upper()} into uploaders!")

    st.markdown("---")
    st.subheader("2. Upload Input Artifacts")
    
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        doc_type = st.selectbox("Document Type", ["Passport (Primary MVP)", "Visa (Extensible Placeholder)", "National ID (Extensible Placeholder)"])
        uploaded_doc = st.file_uploader("Upload Passport / Travel Document Image", type=["png", "jpg", "jpeg"])
        if uploaded_doc is not None:
            st.session_state.passport_img_bytes = uploaded_doc.read()

        if st.session_state.passport_img_bytes:
            st.image(st.session_state.passport_img_bytes, caption="Uploaded Document", use_column_width=True)

    with col_up2:
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded_ver = st.file_uploader("Upload Live Verification Photo (1-to-1 Match)", type=["png", "jpg", "jpeg"])
        if uploaded_ver is not None:
            st.session_state.verification_img_bytes = uploaded_ver.read()

        if st.session_state.verification_img_bytes:
            st.image(st.session_state.verification_img_bytes, caption="Verification Photo", use_column_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Start Screening Action Button
    if st.button("🚀 START AI SCREENING", type="primary", use_container_width=True):
        if not st.session_state.passport_img_bytes:
            st.error("Please upload a passport image or select a preset test case first.")
        else:
            # Run Pipeline with visual indicators
            pipeline_progress = st.empty()

            steps = [
                "📥 Document Uploaded & Preprocessed",
                "🔍 Running OCR Field Extraction...",
                "📄 Validating TD3 MRZ & 7-3-1 Checkdigits...",
                "🛡️ Applying Logical & Watchlist Rules...",
                "🔬 Executing Image Forensics & ELA Tampering Engine...",
                "👤 Performing 1-to-1 Facial Verification...",
                "⚖️ Computing Explainable Risk Score..."
            ]

            for s in steps:
                pipeline_progress.markdown(f"<div class='pipeline-step'>{s}</div>", unsafe_allow_html=True)
                time.sleep(0.15)

            # Process Images
            doc_cv2 = bytes_to_cv2(st.session_state.passport_img_bytes)
            ver_cv2 = bytes_to_cv2(st.session_state.verification_img_bytes) if st.session_state.verification_img_bytes else None

            # 1. OCR & MRZ
            ocr_res = extract_document(doc_cv2, document_type="passport")

            # 2. Validation
            val_res = validate_document(ocr_res)

            # 3. Tampering
            tamp_res = detect_tampering(doc_cv2)

            # 4. Face
            face_res = verify_face(doc_cv2, ver_cv2) if ver_cv2 is not None else {
                "face_detected": False, "match": False, "similarity": 0.0, "confidence": 0.0,
                "message": "No verification photo provided."
            }

            # 5. Risk
            risk_res = calculate_risk(ocr_res, val_res, tamp_res, face_res)

            # Build Combined Report
            report = {
                "screening_id": str(time.time()),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "document": ocr_res,
                "validation": val_res,
                "tampering": tamp_res,
                "face_verification": face_res,
                "risk_assessment": risk_res
            }

            # Save to Database
            save_screening(report)

            pipeline_progress.success("✅ AI Screening Complete! Report Generated Below.")

            st.markdown("---")

            # SCREENING REPORT HEADER BANNER
            level = risk_res["level"]
            score = risk_res["score"]
            badge_class = f"badge-{level.lower()}"

            st.markdown(f"""
            <div style="background-color: #1E293B; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid #334155;">
                <div style="font-size: 1.2rem; color: #94A3B8;">VERIGATE AI FINAL SCREENING RESULT</div>
                <div style="font-size: 2.8rem; font-weight: 900; margin: 10px 0;">
                    RISK SCORE: <span style="color: #38BDF8;">{score}/100</span> — <span class="{badge_class}">{level} RISK</span>
                </div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #E2E8F0;">
                    Recommendation: {risk_res['recommendation']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # TABBED DETAILED RESULTS
            tab_ocr, tab_mrz, tab_val, tab_forensics, tab_face, tab_risk = st.tabs([
                "📋 Identity & OCR", "🔤 MRZ Validation", "✅ Rule Validation",
                "🔬 Image Forensics", "👤 Face Verification", "⚖️ Risk Breakdown"
            ])

            with tab_ocr:
                st.subheader("Extracted Passport Information")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Full Name:** {ocr_res.get('name')}")
                    st.write(f"**Passport Number:** {ocr_res.get('passport_number')}")
                    st.write(f"**Nationality:** {ocr_res.get('nationality')}")
                with col_info2:
                    st.write(f"**Date of Birth:** {ocr_res.get('dob')}")
                    st.write(f"**Gender:** {ocr_res.get('gender')}")
                    st.write(f"**Expiry Date:** {ocr_res.get('expiry')}")
                
                st.metric("OCR Field Extraction Confidence", f"{int(ocr_res.get('confidence', 0.85) * 100)}%")

            with tab_mrz:
                st.subheader("Machine Readable Zone (MRZ) Checksum Analysis")
                mrz = ocr_res.get("mrz", {})
                if mrz.get("mrz_detected"):
                    st.code(f"Line 1: {mrz.get('raw_line1')}\nLine 2: {mrz.get('raw_line2')}", language="text")
                    
                    chk = mrz.get("checksums", {})
                    df_chk = pd.DataFrame([
                        {"Checksum Field": "Passport Number", "Calculated": chk.get("passport_number", {}).get("calculated"), "Expected": chk.get("passport_number", {}).get("expected"), "Status": "✓ PASS" if chk.get("passport_number", {}).get("valid") else "✗ FAIL"},
                        {"Checksum Field": "Date of Birth", "Calculated": chk.get("dob", {}).get("calculated"), "Expected": chk.get("dob", {}).get("expected"), "Status": "✓ PASS" if chk.get("dob", {}).get("valid") else "✗ FAIL"},
                        {"Checksum Field": "Expiry Date", "Calculated": chk.get("expiry", {}).get("calculated"), "Expected": chk.get("expiry", {}).get("expected"), "Status": "✓ PASS" if chk.get("expiry", {}).get("valid") else "✗ FAIL"},
                        {"Checksum Field": "Composite Check", "Calculated": chk.get("composite", {}).get("calculated"), "Expected": chk.get("composite", {}).get("expected"), "Status": "✓ PASS" if chk.get("composite", {}).get("valid") else "✗ FAIL"},
                    ])
                    st.table(df_chk)
                else:
                    st.warning(mrz.get("message", "MRZ could not be detected."))

            with tab_val:
                st.subheader("Document Validation Rules Matrix")
                df_val = pd.DataFrame(val_res.get("checks", []))
                st.dataframe(df_val, use_container_width=True)

            with tab_forensics:
                st.subheader("Document Tampering & ELA Heatmap Analysis")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.image(doc_cv2, caption="Original Uploaded Document", channels="BGR", use_column_width=True)
                with col_f2:
                    heatmap_b64 = tamp_res.get("visualization_heatmap_b64", "")
                    if heatmap_b64:
                        st.image(heatmap_b64, caption="Analyzed Tampering Heatmap Overlay", use_column_width=True)

                st.markdown(f"**Analysis Engine Mode:** `{tamp_res.get('analysis_mode')}`")
                st.write(f"**Tampering Likelihood Score:** `{tamp_res.get('tampering_score')}%`")
                st.write(f"**Suspicious Compression Anomalies Count:** `{tamp_res.get('suspicious_regions_count')}`")
                
                if tamp_res.get("suspicious_regions"):
                    st.caption("Detected suspicious bounding box regions:")
                    st.json(tamp_res.get("suspicious_regions"))

            with tab_face:
                st.subheader("1-to-1 Face Verification Results")
                col_face1, col_face2 = st.columns(2)
                with col_face1:
                    if face_res.get("document_face_b64"):
                        st.image(face_res["document_face_b64"], caption="Extracted Passport Face Crop", width=180)
                    else:
                        st.info("No passport face detected")
                with col_face2:
                    if face_res.get("verification_face_b64"):
                        st.image(face_res["verification_face_b64"], caption="Live Verification Photo Face Crop", width=180)
                    else:
                        st.info("No verification face provided")

                st.write(f"**Facial Similarity Score:** `{face_res.get('similarity')}%`")
                st.write(f"**Verification Engine:** `{face_res.get('engine_used', 'OpenCV')}`")
                
                if face_res.get("match"):
                    st.success("✓ Identity Match Verified!")
                else:
                    st.error("⚠ Identity Mismatch Alert!")

            with tab_risk:
                st.subheader("Explainable Risk Breakdown & Reasons")
                
                # Gauge Chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Overall Risk Score ({level})"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#38BDF8"},
                        'steps': [
                            {'range': [0, 30], 'color': "rgba(52, 211, 153, 0.3)"},
                            {'range': [30, 60], 'color': "rgba(251, 191, 36, 0.3)"},
                            {'range': [60, 100], 'color': "rgba(248, 113, 113, 0.3)"}
                        ],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#E2E8F0', height=250)
                st.plotly_chart(fig_gauge, use_container_width=True)

                st.markdown("#### Primary Flagged Risk Reasons:")
                for r in risk_res.get("reasons", []):
                    st.markdown(f"• **{r}**")

                st.markdown("#### Risk Model Weight Distributions:")
                st.json(risk_res.get("weights_applied"))


# ==========================================
# PAGE 3: AUDIT TRAIL
# ==========================================
elif page == "📜 Screening Audit Trail":
    st.markdown("""
    <div class="header-card">
        <div class="app-title">Screening Audit Trail</div>
        <div class="app-subtitle">Searchable Local Audit Database Records</div>
    </div>
    """, unsafe_allow_html=True)

    recent_screenings = get_recent_screenings(limit=50)
    if recent_screenings:
        df_audit = pd.DataFrame(recent_screenings)
        
        search_query = st.text_input("Filter by Passport Number or Holder Name")
        if search_query:
            df_audit = df_audit[
                df_audit['passport_number'].str.contains(search_query, case=False, na=False) |
                df_audit['holder_name'].str.contains(search_query, case=False, na=False)
            ]
            
        st.dataframe(df_audit, use_container_width=True, height=400)
    else:
        st.info("No audit records found in SQLite database.")


# ==========================================
# PAGE 4: WATCHLIST SEARCH
# ==========================================
elif page == "🚨 Watchlist Search":
    st.markdown("""
    <div class="header-card">
        <div class="app-title">Synthetic Watchlist Lookup</div>
        <div class="app-subtitle">DEMO DATA — NOT A GOVERNMENT DATABASE</div>
    </div>
    """, unsafe_allow_html=True)

    query_pass = st.text_input("Enter Passport Number to query watchlist (Try: X9988776, Z1122334, M5566778)", value="X9988776")
    
    if st.button("Search Watchlist"):
        result = search_watchlist(query_pass)
        if result:
            st.error(f"🚨 ALERT: Match Found in Demo Watchlist!\nStatus: {result['status']}\nReason: {result['reason']}")
            st.json(result)
        else:
            st.success(f"✓ Clear: Passport Number '{query_pass}' not found in demo watchlist.")

# Global Disclaimer Footer
st.markdown("""
<div class="disclaimer-box">
    <b>DISCLAIMER:</b> VeriGate AI is an AI-assisted screening prototype intended to support human verification. 
    It does not replace authorized border, immigration, law-enforcement, or government decision-making. 
    All watchlist and sample records contained herein are synthetic demo data.
</div>
""", unsafe_allow_html=True)
