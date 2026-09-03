import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import DB_PATH


def get_connection():
    """Get SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed initial synthetic demo data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create screenings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screenings (
        screening_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        document_type TEXT NOT NULL,
        passport_number TEXT,
        holder_name TEXT,
        nationality TEXT,
        validation_status TEXT NOT NULL,
        tampering_status TEXT NOT NULL,
        face_match_status TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        raw_result_json TEXT NOT NULL
    );
    """)

    # Create watchlist table (DEMO SYNTHETIC WATCHLIST)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        passport_number TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        status TEXT NOT NULL, -- FLAGGED, EXPIRED, CLEAR
        reason TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Seed demo watchlist if empty
    cursor.execute("SELECT COUNT(*) FROM watchlist")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        demo_records = [
            ("X9988776", "INTERPOL DEMO WATCH", "FLAGGED", "Stolen document reported to Interpol (Demo Data)", now),
            ("Z1122334", "ALICE SMITH", "EXPIRED", "Passport expired and revoked (Demo Data)", now),
            ("M5566778", "JOHN BADACTOR", "FLAGGED", "Security alert demo flag (Demo Data)", now),
        ]
        cursor.executemany(
            "INSERT INTO watchlist (passport_number, full_name, status, reason, updated_at) VALUES (?, ?, ?, ?, ?)",
            demo_records
        )

    conn.commit()
    conn.close()


def save_screening(result_data: Dict[str, Any]) -> str:
    """Save completed screening to SQLite audit log."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    screening_id = result_data.get("screening_id") or str(uuid.uuid4())
    timestamp = result_data.get("timestamp") or datetime.now().isoformat()
    
    doc_info = result_data.get("document", {})
    val_info = result_data.get("validation", {})
    tamp_info = result_data.get("tampering", {})
    face_info = result_data.get("face_verification", {})
    risk_info = result_data.get("risk_assessment", {})

    cursor.execute("""
        INSERT INTO screenings (
            screening_id, timestamp, document_type, passport_number, holder_name,
            nationality, validation_status, tampering_status, face_match_status,
            risk_score, risk_level, recommendation, raw_result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        screening_id,
        timestamp,
        doc_info.get("document_type", "passport"),
        doc_info.get("passport_number", "UNKNOWN"),
        doc_info.get("name", "UNKNOWN"),
        doc_info.get("nationality", "UNKNOWN"),
        "PASS" if val_info.get("is_valid", False) else "FAIL",
        "TAMPERED" if tamp_info.get("tampered", False) else "CLEAR",
        "MATCH" if face_info.get("match", False) else "MISMATCH",
        risk_info.get("score", 0),
        risk_info.get("level", "LOW"),
        risk_info.get("recommendation", "Proceed"),
        json.dumps(result_data)
    ))

    conn.commit()
    conn.close()
    return screening_id


def get_screening_by_id(screening_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full screening report by screening ID."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT raw_result_json FROM screenings WHERE screening_id = ?", (screening_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row["raw_result_json"])
    return None


def get_recent_screenings(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent screenings summary list for dashboard."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT screening_id, timestamp, document_type, passport_number, holder_name,
               nationality, validation_status, tampering_status, face_match_status,
               risk_score, risk_level, recommendation
        FROM screenings
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_watchlist(passport_number: str) -> Optional[Dict[str, Any]]:
    """Search synthetic watchlist database for matching passport number."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlist WHERE passport_number = ?", (passport_number.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_screening_stats() -> Dict[str, Any]:
    """Calculate dashboard summary stats."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM screenings")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'LOW'")
    low = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'MEDIUM'")
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'HIGH'")
    high = cursor.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "low_risk": low,
        "medium_risk": medium,
        "high_risk": high
    }
