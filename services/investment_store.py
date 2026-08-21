"""Durable SQLite history of finished analyses."""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from config import config


_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    address TEXT,
    city TEXT,
    decision TEXT,
    priority TEXT,
    human_decision TEXT,
    overall_score REAL,
    risk_score REAL,
    report_json TEXT
)
"""


class InvestmentStore:
    def __init__(self):
        self.db_path = config.investment_db_path

    def save_analysis(self, state: Dict[str, Any]) -> None:
        record = state.get("property") or {}
        report = state.get("report") or {}
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(_SCHEMA)
            connection.execute(
                """
                INSERT OR REPLACE INTO analyses
                (analysis_id, created_at, address, city, decision, priority,
                 human_decision, overall_score, risk_score, report_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.get("analysis_id", ""),
                    datetime.now().isoformat(timespec="seconds"),
                    record.get("address", ""),
                    record.get("city", ""),
                    report.get("decision", state.get("decision", "")),
                    report.get("priority", state.get("priority", "")),
                    state.get("human_decision", ""),
                    float(state.get("overall_score", 0.0) or 0.0),
                    float(state.get("risk_score", 0.0) or 0.0),
                    json.dumps(report, default=str),
                ),
            )

    def list_analyses(self, limit: int = 20) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute(_SCHEMA)
            rows = connection.execute(
                """
                SELECT analysis_id, created_at, address, city, decision, priority,
                       human_decision, overall_score, risk_score
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


investment_store = InvestmentStore()
