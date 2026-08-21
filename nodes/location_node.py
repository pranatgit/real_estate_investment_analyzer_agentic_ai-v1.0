"""LangGraph node for location_node analysis."""

from typing import Any, Dict

from agents.location_agent import LocationAgent


def location_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("decision") == "PASS":
        return {}
    try:
        results = LocationAgent().analyze(state.get("property") or {})
        return {"location_results": results}
    except Exception as exc:
        return {"errors": [{"node": "location_node", "error": str(exc)}]}
