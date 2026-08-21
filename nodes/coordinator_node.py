"""Deterministic aggregation node."""

from typing import Any, Dict, Iterable

from config import config


def _first(results):
    return results[0] if results else {}


def _score(result: Dict[str, Any], key: str) -> float:
    try:
        return max(0.0, min(10.0, float(result.get(key, 0.0))))
    except (TypeError, ValueError):
        return 0.0


def _limited(items: Iterable[Any], limit: int = 8):
    return [item for item in items if item not in (None, "")][:limit]


def coordinator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    location = _first(state.get("location_results") or [])
    price = _first(state.get("price_results") or [])
    market = _first(state.get("market_results") or [])
    condition = _first(state.get("condition_results") or [])
    roi = _first(state.get("roi_results") or [])

    component_scores = {
        "location": _score(location, "location_score"),
        "price": _score(price, "pricing_score"),
        "market": _score(market, "market_score"),
        "condition": _score(condition, "condition_score"),
        "roi": _score(roi, "roi_score"),
    }

    overall = (
        component_scores["location"] * config.location_weight
        + component_scores["price"] * config.price_weight
        + component_scores["market"] * config.market_weight
        + component_scores["condition"] * config.condition_weight
        + component_scores["roi"] * config.roi_weight
    )
    overall = round(max(0.0, min(10.0, overall)), 2)

    risk = round(max(0.0, min(10.0, _score(roi, "risk_score"))), 2)

    findings = _limited(
        list(location.get("insights") or [])
        + list(roi.get("insights") or [])
        + list(condition.get("recommendations") or []),
        8,
    )

    summary = {
        "component_scores": component_scores,
        "annual_roi": roi.get("annual_roi", 0.0),
        "monthly_cash_flow": roi.get("monthly_cash_flow", 0.0),
        "cap_rate": roi.get("cap_rate", 0.0),
        "cash_on_cash": roi.get("cash_on_cash", 0.0),
        "ai_recommendation": roi.get("ai_recommendation", ""),
        "location_tier": location.get("tier", ""),
        "price_verdict": price.get("verdict", ""),
        "market_temperature": market.get("temperature", ""),
        "condition_tier": condition.get("tier", ""),
        "risk_factors": list(roi.get("risk_factors") or []),
        "negotiation_points": list(price.get("negotiation_points") or []),
        "key_findings": findings,
    }

    return {
        "overall_score": overall,
        "risk_score": risk,
        "coordination_summary": summary,
    }
