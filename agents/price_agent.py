"""LLM-powered property pricing/appraisal agent."""

import json
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.gemini_service import as_number, get_gemini_service


class PriceAgent(BaseAgent):
    def analyze(self, property_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        service = get_gemini_service()
        prompt = f"""
You are a real-estate appraiser and investment pricing analyst.

Estimate market value from the comparable properties plus the subject property's
size and type. Judge the asking price against the estimated value. Do not invent
comparable sales or market facts. If evidence is limited, state that limitation
in negotiation_points.

PROPERTY:
{json.dumps(property_record, indent=2, default=str)}
"""
        schema = {
            "estimated_value": "number in currency",
            "price_to_value": "number; asking price divided by estimated value",
            "verdict": "short label such as UNDERVALUED, FAIR, OVERVALUED",
            "pricing_score": "number 0-10 where higher is better priced",
            "negotiation_points": ["string"],
        }
        raw = service.analyze_with_structured_output(prompt, schema)
        return [{
            "estimated_value": round(as_number(raw.get("estimated_value")), 2),
            "price_to_value": round(as_number(raw.get("price_to_value")), 3),
            "verdict": str(raw.get("verdict", "")).strip(),
            "pricing_score": round(max(0.0, min(10.0, as_number(raw.get("pricing_score")))), 1),
            "negotiation_points": list(raw.get("negotiation_points") or []),
        }]
