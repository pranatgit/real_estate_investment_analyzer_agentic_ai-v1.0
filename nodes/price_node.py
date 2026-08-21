"""LangGraph node for price_node analysis."""

from typing import Any, Dict

from agents.price_agent import PriceAgent


def price_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("decision") == "PASS":
        return {}
    try:
        results = PriceAgent().analyze(state.get("property") or {})
        return {"price_results": results}
    except Exception as exc:
        return {"errors": [{"node": "price_node", "error": str(exc)}]}
