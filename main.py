"""Application logic and Streamlit entry point."""

import uuid
from typing import Any, Dict

from config import validate_config
from human_intervention.approval_manager import approve_analysis, override_analysis
from services.investment_store import investment_store
from workflow import build_investment_workflow
from streamlit_UI import render_app


_workflow = build_investment_workflow()


def _initial_state(analysis_id: str, property_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "analysis_id": analysis_id,
        "property": property_record,
        "location_results": [],
        "price_results": [],
        "market_results": [],
        "condition_results": [],
        "roi_results": [],
        "coordination_summary": {},
        "overall_score": 0.0,
        "risk_score": 0.0,
        "decision": "",
        "priority": "",
        "risk_level": "",
        "decision_metrics": {},
        "human_decision": "",
        "report": {},
        "workflow_complete": False,
        "errors": [],
    }


def _thread_config(thread_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def run_analysis(property_record: Dict[str, Any]) -> Dict[str, Any]:
    validate_config()
    analysis_id = f"INV-{uuid.uuid4().hex[:10].upper()}"
    initial = _initial_state(analysis_id, property_record)

    values = _workflow.invoke(initial, config=_thread_config(analysis_id))
    interrupted = bool(values.get("__interrupt__"))
    interrupt_payload = None

    if interrupted:
        interrupt_payload = values["__interrupt__"][0].value
    else:
        investment_store.save_analysis(values)

    return {
        "values": values,
        "interrupted": interrupted,
        "interrupt_payload": interrupt_payload,
        "thread_id": analysis_id,
    }


def approve_decision(thread_id: str) -> Dict[str, Any]:
    final_state = approve_analysis(_workflow, thread_id)
    investment_store.save_analysis(final_state)
    return final_state


def override_decision(thread_id: str) -> Dict[str, Any]:
    final_state = override_analysis(_workflow, thread_id)
    investment_store.save_analysis(final_state)
    return final_state


render_app(
    run_analysis,
    approve_decision,
    override_decision,
    investment_store.list_analyses,
)
