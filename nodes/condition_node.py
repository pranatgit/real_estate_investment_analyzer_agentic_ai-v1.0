"""LangGraph node for condition_node analysis."""

from typing import Any, Dict

from agents.property_condition_agent import PropertyConditionAgent


def condition_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("decision") == "PASS":
        return {}
    try:
        results = PropertyConditionAgent().analyze(state.get("property") or {})
        return {"condition_results": results}
    except Exception as exc:
        return {"errors": [{"node": "condition_node", "error": str(exc)}]}
