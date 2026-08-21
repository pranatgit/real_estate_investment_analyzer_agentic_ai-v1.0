"""Human-in-the-loop analyst gate."""

from typing import Any, Dict

from langgraph.types import interrupt


def analyst_review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    summary = state.get("coordination_summary") or {}
    payload = {
        "analysis_id": state.get("analysis_id", ""),
        "decision": state.get("decision", ""),
        "priority": state.get("priority", ""),
        "risk_level": state.get("risk_level", ""),
        "metrics": state.get("decision_metrics", {}),
        "overall_score": state.get("overall_score", 0.0),
        "question": "Please sign off on the recommendation or override it.",
    }

    response = interrupt(payload)
    action = response.get("action") if isinstance(response, dict) else response
    if action not in {"approve", "override"}:
        # An invalid resume is treated as an override rather than silently
        # approving capital deployment.
        action = "override"

    return {"human_decision": action}
