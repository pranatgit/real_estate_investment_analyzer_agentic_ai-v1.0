"""LLM-powered location analysis agent."""

import json
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.gemini_service import as_number, get_gemini_service


class LocationAgent(BaseAgent):
    def analyze(self, property_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        service = get_gemini_service()
        prompt = f"""
You are the location analyst in a real-estate investment underwriting workflow.

Evaluate the property's neighborhood using only the supplied record. Consider:
- address/city/state
- school rating
- crime rating
- walkability and transit scores
- amenities
- commute time

Score location quality from 0 to 10. Do not invent missing facts. Return concise,
investment-oriented insights.

PROPERTY:
{json.dumps(property_record, indent=2, default=str)}
"""
        schema = {
            "location_score": "number 0-10",
            "tier": "short label such as EXCELLENT, GOOD, AVERAGE, BELOW_AVERAGE, POOR",
            "insights": ["string"],
            "investment_potential": "short explanation",
        }
        raw = service.analyze_with_structured_output(prompt, schema)
        result = {
            "location_score": round(max(0.0, min(10.0, as_number(raw.get("location_score")))), 1),
            "tier": str(raw.get("tier", "")).strip(),
            "insights": list(raw.get("insights") or []),
            "investment_potential": str(raw.get("investment_potential", "")).strip(),
        }
        return [result]
