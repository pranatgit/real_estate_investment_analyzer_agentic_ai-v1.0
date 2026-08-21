"""LangGraph topology for the Real Estate Investment Analyzer."""

from langgraph.graph import END, START, StateGraph

from state import InvestmentState
from nodes.analyst_review_node import analyst_review_node
from nodes.condition_node import condition_node
from nodes.coordinator_node import coordinator_node
from nodes.decision_node import decision_node
from nodes.location_node import location_node
from nodes.market_node import market_node
from nodes.price_node import price_node
from nodes.report_node import report_node
from nodes.roi_node import roi_node
from nodes.validation_node import validation_node


STAGE1_NODES = [
    "location_analysis",
    "price_analysis",
    "market_analysis",
    "condition_analysis",
]


def route_after_decision(state: InvestmentState) -> str:
    return "report" if state.get("decision") == "PASS" else "analyst_review"


def build_investment_graph() -> StateGraph:
    graph = StateGraph(InvestmentState)

    graph.add_node("validate", validation_node)
    graph.add_node("location_analysis", location_node)
    graph.add_node("price_analysis", price_node)
    graph.add_node("market_analysis", market_node)
    graph.add_node("condition_analysis", condition_node)
    graph.add_node("roi_analysis", roi_node)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("decision", decision_node)
    graph.add_node("analyst_review", analyst_review_node)
    graph.add_node("report", report_node)

    graph.add_edge(START, "validate")

    for node in STAGE1_NODES:
        graph.add_edge("validate", node)

    # Fan-in: ROI has all four Stage-1 nodes as predecessors, so it cannot
    # execute until all four have completed.
    graph.add_edge(STAGE1_NODES, "roi_analysis")

    graph.add_edge("roi_analysis", "coordinator")
    graph.add_edge("coordinator", "decision")

    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        ["report", "analyst_review"],
    )

    graph.add_edge("analyst_review", "report")
    graph.add_edge("report", END)

    return graph
