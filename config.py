"""Central configuration for the Real Estate Investment Analyzer."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class SystemConfig:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    data_dir: str = str(PROJECT_ROOT / "data")
    investment_db_path: str = str(PROJECT_ROOT / "investments.db")
    checkpoint_db_path: str = str(PROJECT_ROOT / "checkpoints.db")

    location_weight: float = 0.25
    price_weight: float = 0.20
    market_weight: float = 0.20
    condition_weight: float = 0.15
    roi_weight: float = 0.20

    strong_buy_score: float = 8.0
    buy_score: float = 7.0
    consider_score: float = 6.0
    location_threshold: float = 7.0
    min_roi: float = 8.0
    strong_roi_multiple: float = 1.5
    consider_roi_multiple: float = 0.75
    strong_cash_flow: float = 500.0
    max_risk: float = 6.0

    high_risk: float = 6.0
    moderate_risk: float = 4.0


config = SystemConfig()

REQUIRED_FIELDS = ["address", "listing_price", "square_footage", "year_built"]

PRIORITY = {
    "STRONG_BUY": "HIGH",
    "BUY": "MEDIUM",
    "CONSIDER": "MEDIUM",
    "PASS": "LOW",
}

ACTION_ITEMS = {
    "STRONG_BUY": ["Analyst sign-off required, then move to offer"],
    "BUY": ["Analyst sign-off required before making an offer"],
    "CONSIDER": ["Analyst review - proceed only with the noted conditions"],
    "PASS": ["No action - file the record"],
}


def validate_config() -> bool:
    if not config.gemini_api_key or config.gemini_api_key.lower().startswith("your"):
        raise ValueError("GEMINI_API_KEY is missing. Paste your key into the .env file.")
    if not config.gemini_model:
        raise ValueError("GEMINI_MODEL is missing. Set it in the .env file.")
    return True
