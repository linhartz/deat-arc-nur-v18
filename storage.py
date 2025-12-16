# storage.py
import sqlite3
import json
import time
from typing import Dict, Any

DB_PATH = "experiment.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        event_label TEXT,
        arc_cn REAL,
        arc_ru REAL,
        arc_us REAL,
        chaotic_risk REAL,
        nur_score REAL,
        arc_reliability REAL,
        survival INTEGER,
        assets_json TEXT,
        air_json TEXT,
        rsz_json TEXT
    )
    """)
    conn.commit()
    conn.close()


def log_experiment(
    event_label: str,
    arc: Dict[str, float],
    chaotic_risk: float,
    nur_result: Dict[str, Any],
    assets: Dict[str, Any],
    air: Dict[str, Any] = None,
    rsz: Dict[str, Any] = None
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    INSERT INTO experiments (
        timestamp,
        event_label,
        arc_cn,
        arc_ru,
        arc_us,
        chaotic_risk,
        nur_score,
        arc_reliability,
        survival,
        assets_json,
        air_json,
        rsz_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        time.time(),
        event_label,
        arc["CN"],
        arc["RU"],
        arc["US"],
        chaotic_risk,
        nur_result["nur_score"],
        nur_result["arc_reliability"],
        int(nur_result["survival"]),
        json.dumps(assets),
        json.dumps(air or {}),
        json.dumps(rsz or {})
    ))

    conn.commit()
    conn.close()
