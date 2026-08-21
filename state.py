"""Shared LangGraph state for the Real Estate Investment Analyzer."""

import operator
from typing import Annotated, Any, Dict, List, TypedDict


class InvestmentState(TypedDict):
    analysis_id: str
    property: Dict[str, Any]

    location_results: List[Dict[str, Any]]
    price_results: List[Dict[str, Any]]
    market_results: List[Dict[str, Any]]
    condition_results: List[Dict[str, Any]]
    roi_results: List[Dict[str, Any]]

    coordination_summary: Dict[str, Any]
    overall_score: float
    risk_score: float

    decision: str
    priority: str
    risk_level: str
    decision_metrics: Dict[str, Any]

    human_decision: str
    report: Dict[str, Any]
    workflow_complete: bool

    errors: Annotated[List[Dict[str, Any]], operator.add]
