"""Ordered four-band investment decision ladder."""

from typing import Any, Dict

from config import PRIORITY, config


def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Preserve the validation sentinel. Once a record is unassessable, it must
    # never become an actionable recommendation later in the graph.
    if state.get("decision") == "PASS" and not state.get("coordination_summary"):
        decision = "PASS"
    else:
        summary = state.get("coordination_summary") or {}
        components = summary.get("component_scores") or {}
        overall = float(state.get("overall_score", 0.0) or 0.0)
        risk = float(state.get("risk_score", 0.0) or 0.0)
        annual_roi = float(summary.get("annual_roi", 0.0) or 0.0)
        cash_flow = float(summary.get("monthly_cash_flow", 0.0) or 0.0)
        location = float(components.get("location", 0.0) or 0.0)

        if (
            overall >= config.strong_buy_score
            and annual_roi >= config.min_roi * config.strong_roi_multiple
            and location >= config.location_threshold
            and cash_flow > config.strong_cash_flow
            and risk <= config.max_risk
        ):
            decision = "STRONG_BUY"
        elif (
            overall >= config.buy_score
            and annual_roi >= config.min_roi
            and location >= config.location_threshold - 1
            and risk <= config.max_risk
        ):
            decision = "BUY"
        elif (
            overall >= config.consider_score
            and annual_roi >= config.min_roi * config.consider_roi_multiple
        ):
            decision = "CONSIDER"
        else:
            decision = "PASS"

    priority = PRIORITY.get(decision, PRIORITY["PASS"])
    risk_score = float(state.get("risk_score", 0.0) or 0.0)
    if risk_score >= config.high_risk:
        risk_level = "HIGH"
    elif risk_score >= config.moderate_risk:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    summary = state.get("coordination_summary") or {}
    metrics = {
        "overall_score": round(float(state.get("overall_score", 0.0) or 0.0), 2),
        "risk_score": round(risk_score, 2),
        "component_scores": summary.get("component_scores", {}),
        "annual_roi": summary.get("annual_roi", 0.0),
        "monthly_cash_flow": summary.get("monthly_cash_flow", 0.0),
        "cap_rate": summary.get("cap_rate", 0.0),
    }

    return {
        "decision": decision,
        "priority": priority,
        "risk_level": risk_level,
        "decision_metrics": metrics,
    }
