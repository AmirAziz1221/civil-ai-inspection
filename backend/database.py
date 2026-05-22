import os
import json
import sqlite3
from typing import List, Optional, Dict, Any
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "inspections.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id TEXT PRIMARY KEY,
                image_id TEXT,
                original_filename TEXT,
                model_name TEXT,
                asset_type TEXT,
                detections TEXT,
                annotated_image TEXT,
                total_defects INTEGER,
                severity_summary TEXT,
                overall_severity TEXT,
                engineer_notes TEXT,
                ai_report TEXT,
                report_docx TEXT,
                report_pdf TEXT,
                created_at TEXT
            )
        """)
        conn.commit()


def save_inspection(data: Dict[str, Any]):
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM inspections WHERE id = ?", (data["id"],)).fetchone()
        if existing:
            conn.execute("""
                UPDATE inspections SET
                    image_id = ?, original_filename = ?, model_name = ?, asset_type = ?,
                    detections = ?, annotated_image = ?, total_defects = ?,
                    severity_summary = ?, overall_severity = ?, engineer_notes = ?,
                    ai_report = ?, report_docx = ?, report_pdf = ?, created_at = ?
                WHERE id = ?
            """, (
                data.get("image_id", ""),
                data.get("original_filename", ""),
                data.get("model_name", ""),
                data.get("asset_type", ""),
                json.dumps(data.get("detections", [])),
                data.get("annotated_image", ""),
                data.get("total_defects", 0),
                json.dumps(data.get("severity_summary", {})),
                data.get("overall_severity", ""),
                data.get("engineer_notes", ""),
                json.dumps(data.get("ai_report", {})),
                data.get("report_docx", ""),
                data.get("report_pdf", ""),
                data.get("created_at", ""),
                data["id"]
            ))
        else:
            conn.execute("""
                INSERT INTO inspections VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data["id"],
                data.get("image_id", ""),
                data.get("original_filename", ""),
                data.get("model_name", ""),
                data.get("asset_type", ""),
                json.dumps(data.get("detections", [])),
                data.get("annotated_image", ""),
                data.get("total_defects", 0),
                json.dumps(data.get("severity_summary", {})),
                data.get("overall_severity", ""),
                data.get("engineer_notes", ""),
                json.dumps(data.get("ai_report", {})),
                data.get("report_docx", ""),
                data.get("report_pdf", ""),
                data.get("created_at", "")
            ))
        conn.commit()


def get_all_inspections() -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM inspections ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_inspection_by_id(inspection_id: str) -> Optional[Dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM inspections WHERE id = ?", (inspection_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def _row_to_dict(row) -> Dict:
    d = dict(row)
    for key in ["detections", "severity_summary", "ai_report"]:
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except Exception:
                d[key] = {}
    return d
