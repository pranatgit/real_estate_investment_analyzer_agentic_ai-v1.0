"""Stage-2 LLM-powered return and independent downside agent."""

import json
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from services.gemini_service import as_number, get_gemini_service


class ROIAgent(BaseAgent):
    def analyze(
        self,
        property_record: Dict[str, Any],
        location: Dict[str, Any],
        price: Dict[str, Any],
        market: Dict[str, Any],
        condition: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        service = get_gemini_service()
        prompt = f"""
You are the senior investment analyst in a real-estate underwriting workflow.

Use the property financials and the four completed Stage-1 analyses below.
Work out the investment returns and then make an INDEPENDENT downside/risk
assessment. The risk score is 0-10 where HIGHER MEANS RISKIER.

Do not derive risk from the quality score and do not calculate risk as
10 - roi_score or 10 - overall_score. Identify concrete risks such as weak
cash flow, expensive debt, overvaluation, repairs, thin comparables, cooling
market, or other facts actually supported by the record.

PROPERTY:
{json.dumps(property_record, indent=2, default=str)}

LOCATION:
{json.dumps(location, indent=2, default=str)}

PRICE:
{json.dumps(price, indent=2, default=str)}

MARKET:
{json.dumps(market, indent=2, default=str)}

CONDITION:
{json.dumps(condition, indent=2, default=str)}
"""
        schema = {
            "annual_roi": "percentage number",
            "monthly_cash_flow": "currency number",
            "cap_rate": "percentage number",
            "cash_on_cash": "percentage number",
            "roi_score": "number 0-10",
            "risk_score": "number 0-10 where higher is riskier",
            "risk_factors": ["concrete risk strings"],
            "ai_recommendation": "short recommendation",
            "insights": ["investment insight strings"],
        }
        raw = service.analyze_with_structured_output(prompt, schema)
        return [{
            "annual_roi": round(as_number(raw.get("annual_roi")), 2),
            "monthly_cash_flow": round(as_number(raw.get("monthly_cash_flow")), 2),
            "cap_rate": round(as_number(raw.get("cap_rate")), 2),
            "cash_on_cash": round(as_number(raw.get("cash_on_cash")), 2),
            "roi_score": round(max(0.0, min(10.0, as_number(raw.get("roi_score")))), 1),
            "risk_score": round(max(0.0, min(10.0, as_number(raw.get("risk_score")))), 1),
            "risk_factors": list(raw.get("risk_factors") or []),
            "ai_recommendation": str(raw.get("ai_recommendation", "")).strip(),
            "insights": list(raw.get("insights") or []),
        }]
