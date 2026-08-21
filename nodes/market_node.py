"""LangGraph node for market_node analysis."""

from typing import Any, Dict

from agents.market_trends_agent import MarketTrendsAgent


def market_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("decision") == "PASS":
        return {}
    try:
        results = MarketTrendsAgent().analyze(state.get("property") or {})
        return {"market_results": results}
    except Exception as exc:
        return {"errors": [{"node": "market_node", "error": str(exc)}]}
