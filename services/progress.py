import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "progress.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            speaker_id TEXT NOT NULL,
            ts TEXT NOT NULL,
            target_lang TEXT,
            detected_lang TEXT,
            transcript TEXT,
            weakest_point TEXT,
            num_issues INTEGER,
            llm_model TEXT
        )
        """)
        conn.commit()
    finally:
        conn.close()

def save_attempt(speaker_id: str, ts: str, target_lang: str, detected_lang: str,
                 transcript: str, weakest_point: str, num_issues: int, llm_model: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            INSERT INTO attempts (speaker_id, ts, target_lang, detected_lang, transcript, weakest_point, num_issues, llm_model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (speaker_id, ts, target_lang, detected_lang, transcript, weakest_point, int(num_issues), llm_model))
        conn.commit()
    finally:
        conn.close()

def load_attempts(speaker_id: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(
            "SELECT ts, target_lang, detected_lang, num_issues, weakest_point, llm_model FROM attempts WHERE speaker_id=? ORDER BY id DESC LIMIT 50",
            conn,
            params=(speaker_id,)
        )
        return df
    finally:
        conn.close()
