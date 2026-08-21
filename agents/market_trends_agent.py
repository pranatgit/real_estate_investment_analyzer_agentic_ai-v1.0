"""LLM-powered local market trends agent."""

import json
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.gemini_service import as_number, get_gemini_service


class MarketTrendsAgent(BaseAgent):
    def analyze(self, property_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        service = get_gemini_service()
        prompt = f"""
You are a local real-estate market analyst.

Read the supplied price history, average days on market, inventory, and price
reductions. Assess market direction and temperature. Do not invent external
data. Score the current market from 0 to 10 for an investor.

PROPERTY:
{json.dumps(property_record, indent=2, default=str)}
"""
        schema = {
            "market_score": "number 0-10",
            "temperature": "short label such as HOT, WARM, STABLE, COOL, COLD",
            "trend_direction": "short label such as UP, FLAT, DOWN",
            "annual_appreciation": "percentage number",
            "forecast": "short explanation",
        }
        raw = service.analyze_with_structured_output(prompt, schema)
        return [{
            "market_score": round(max(0.0, min(10.0, as_number(raw.get("market_score")))), 1),
            "temperature": str(raw.get("temperature", "")).strip(),
            "trend_direction": str(raw.get("trend_direction", "")).strip(),
            "annual_appreciation": round(as_number(raw.get("annual_appreciation")), 2),
            "forecast": str(raw.get("forecast", "")).strip(),
        }]
