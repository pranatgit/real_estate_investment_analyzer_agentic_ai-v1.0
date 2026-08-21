"""LLM-powered property condition/inspection agent."""

import json
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.gemini_service import as_number, get_gemini_service


class PropertyConditionAgent(BaseAgent):
    def analyze(self, property_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        service = get_gemini_service()
        prompt = f"""
You are a property inspector underwriting an investment purchase.

Assess the property's age, overall condition, component conditions, recent
updates, and known issues. Score condition from 0 to 10. Estimate immediate
repair needs and annual maintenance. Never invent an issue that is not supported
by the record.

PROPERTY:
{json.dumps(property_record, indent=2, default=str)}
"""
        schema = {
            "condition_score": "number 0-10",
            "tier": "short label such as EXCELLENT, GOOD, FAIR, POOR",
            "immediate_repairs": "number in currency",
            "annual_maintenance": "number in currency",
            "recommendations": ["string"],
        }
        raw = service.analyze_with_structured_output(prompt, schema)
        return [{
            "condition_score": round(max(0.0, min(10.0, as_number(raw.get("condition_score")))), 1),
            "tier": str(raw.get("tier", "")).strip(),
            "immediate_repairs": round(as_number(raw.get("immediate_repairs")), 2),
            "annual_maintenance": round(as_number(raw.get("annual_maintenance")), 2),
            "recommendations": list(raw.get("recommendations") or []),
        }]
