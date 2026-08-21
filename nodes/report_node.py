"""Final report assembly node."""

from typing import Any, Dict

from config import ACTION_ITEMS


def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    record = state.get("property") or {}
    summary = state.get("coordination_summary") or {}
    human = state.get("human_decision", "")
    decision = state.get("decision", "PASS")

    if human == "approve":
        final_decision = f"{decision}_confirmed"
    elif human == "override":
        final_decision = "analyst_overridden"
    else:
        final_decision = decision

    report = {
        "analysis_id": state.get("analysis_id", ""),
        "address": record.get("address", ""),
        "city": record.get("city", ""),
        "state": record.get("state", ""),
        "listing_price": record.get("listing_price", 0.0),
        "priority": state.get("priority", ""),
        "risk_level": state.get("risk_level", ""),
        "overall_score": state.get("overall_score", 0.0),
        "risk_score": state.get("risk_score", 0.0),
        "decision": final_decision,
        "decision_metrics": state.get("decision_metrics", {}),
        "annual_roi": summary.get("annual_roi", 0.0),
        "monthly_cash_flow": summary.get("monthly_cash_flow", 0.0),
        "cap_rate": summary.get("cap_rate", 0.0),
        "cash_on_cash": summary.get("cash_on_cash", 0.0),
        "location_tier": summary.get("location_tier", ""),
        "price_verdict": summary.get("price_verdict", ""),
        "market_temperature": summary.get("market_temperature", ""),
        "condition_tier": summary.get("condition_tier", ""),
        "key_findings": list(summary.get("key_findings") or []),
        "risk_factors": list(summary.get("risk_factors") or []),
        "negotiation_points": list(summary.get("negotiation_points") or []),
        "action_items": list(ACTION_ITEMS.get(decision, ACTION_ITEMS["PASS"])),
    }
    return {"report": report, "workflow_complete": True}
