"""Stage-2 ROI node. It waits for all four Stage-1 results via graph topology."""

from typing import Any, Dict

from agents.roi_agent import ROIAgent


def roi_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("decision") == "PASS":
        return {}

    try:
        location = (state.get("location_results") or [])[0]
        price = (state.get("price_results") or [])[0]
        market = (state.get("market_results") or [])[0]
        condition = (state.get("condition_results") or [])[0]

        results = ROIAgent().analyze(
            state.get("property") or {},
            location,
            price,
            market,
            condition,
        )
        return {"roi_results": results}
    except Exception as exc:
        return {"errors": [{"node": "roi_analysis", "error": str(exc)}]}
