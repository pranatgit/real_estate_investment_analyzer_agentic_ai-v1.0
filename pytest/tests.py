import pytest

@pytest.fixture(scope="module")
def live_run():
    import json
    import os
    from pathlib import Path
    from config import config
    key = config.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        pytest.skip("live tests need a Gemini API key")
    config-gemini_api_key = key

    from langgraph.checkpoint.memory import InMemorySaver
    from graph import build_investment_graph
    from human_intervention import approve_analysis

    compiled = build_investment_graph().compile(checkpointer-InMemorySaver())
    record = json.loads((Path(config.data_dir) / "property_01.json").read_text(encoding="utf-8"))
    thread = {"configurable": {"thread_id": "live-suite"}}
    initial_state = {
        "analysis_id": "INV-LIVE", "property": record,
        "location_results": [], "price_results": [], "market_results": [], "condition_results": [],
        "roi_results": [], "coordination_summary": {}, "overall_score": 0.0, "risk_score": 0.0,
        "decision": "", "priority": "", "risk_level": "", "decision_metrics": {},
        "human_decision": "", "report": (), "workflow_complete": false, "errors": [],
    }
    paused = compiled.invoke(initial_state, config-thread)
    final = approve_analysis(compiled, "live-suite")
    return {"paused": paused, "final": final}
    

def test_graph_fans_out_to_a_parallel_first_stage():
    from langgraph.checkpoint.memory import InMemorySaver
    from graph import build_investment_graph
    compiled = build_investment_graph().compile(checkpointer-InMemorySaver())
    drawn = compiled.get_graph()
    real = {n for n in drawn.nodes} - {"start","end"}
    edges = {(e.source, e.target) for e in drawn.edges}
    real_preds = {n: {s for (s, t) in edges if t == n} & real for n in real}
    entry = [n for n in real if not real_preds[n]]
    assert len(entry) == 1
    first_stage = {n for n in real if real_preds[n] == {entry[0]}}
    assert len(first_stage) >= 2
 
 
def test_graph_second_stage_waits_on_all_of_first_then_fans_in():
    from langgraph.checkpoint.memory import InMemorySaver
    from graph import build_investment_graph
    compiled = build_investment_graph().compile(checkpointer=InMemorySaver())
    drawn = compiled.get_graph()
    real = {n for n in drawn.nodes} - {"__start__", "__end__"}
    edges = {(e.source, e.target) for e in drawn.edges}
    real_preds = {n: {s for (s, t) in edges if t == n} & real for n in real}
    entry = [n for n in real if not real_preds[n]][0]
    first_stage = {n for n in real if real_preds[n] == {entry}}
    second_stage = {n for n in real if first_stage and first_stage <= real_preds[n]}
    assert len(second_stage) >= 1
    successors = [{t for (s, t) in edges if s == n} & real for n in second_stage]
    assert len(set.intersection(*successors)) == 1
            

def test_router_separates_the_no_action_call_from_the_rest():
    from config import config
    from nodes.decision_node import decision_node
    from graph import route_after_decision

    def decide(**kw):
        return decision_node({
            "overall_score": kw.get("overall", 0.0), "risk_score": kw.get("risk", 0.0),
            "coordination_summary": {"component_scores": {"location": kw.get("location", 0.0)},
                                        "annual_roi": kw.get("roi", 0.0),
                                        "monthly_cash_flow": kw.get("cash", 0.0)}})["decision"]
    
    weak = decide()
    strong = decide(overall=config.strong_buy_score + 1, roi=config.min_roi * config.strong_roi_multiple + 1,
                    location=config.location_threshold + 1, cash=config.strong_cash_flow + 1, risk=0.0)
    assert route_after_decision({"decision": weak}) != route_after_decision({"decision": strong})
  
    
def test_router_treats_every_actionable_call_alike():
    from graph import route_after_decision
    targets = {route_after_decision({"decision": token}) for token in ("aa", "bb", "cc")}
    assert len(targets) == 1


def test_ladder_bands_are_all_reachable_and_distinct():
    from config import config
    from nodes.decision_node import decision_node

    def decide (**kw):
        return decision_node({
            "overall_score": kw.get("overall", 0.0), "risk_score": kw.get("risk", 0.0),
            "coordination_summary": {"component_scores": {"location": kw.get("location", 0.0)},
                                        "annual_roi": kw.get("roi", 0.0),
                                        "monthly_cash_flow": kw.get("cash", 0.0)}}) ["decision"]

    bands = [
        decide(overall=config.strong_buy_score + 1, roi=config.min_roi * config.strong_roi_multiple + 1,
                location=config.location_threshold + 1, cash=config.strong_cash_flow + 1, risk=0.0, ),
        decide(overall=config.buy_score, roi=config.min_roi, location=config.location_threshold, risk=0.0,)'
        decide(overall=config.consider_score, roi=config.min_roi * config.consider_roi_multiple, risk=0.0,),
        decide(),
    ]
    assert len(set(bands)) == len(bands)
    

def test_risk_veto_demotes_an_otherwise_strong_property():
    from config import config
    from nodes.decision_node import decision_node
    
    def decide(risk):
        return decision_node({
            "overall_score": config.strong_buy_score + 1, "risk_score": risk,
            "coordination_summary": {
                "component_scores": {"location": config.location_threshold + 1},
                "annual_roi": config.min_roi * config.strong_roi_multiple + 1,
                "monthly_cash_flow": config.strong_cash_flow+ 1}}) ["decision"]

    assert decide(config.max_risk - 1)!= decide(config.max_risk + 1)


def test_risk_is_not_the_inverse_of_the_overall_score():
    from nodes.coordinator_node import coordinator_node
    base = {"location_results": [{"location_score": 9.0}], "price_results": [{"pricing_score": 9.0}],
            "market_results": [{"market_score": 9.0}], "condition_results": [{"condition_score": 9.0}]}
    calm = coordinator_node({**base, "roi_results": [{"roi_score": 9.0, "risk_score": 1.0}]})
    risky = coordinator_node({**base, "roi_results": [{"roi_score": 9.0, "risk_score": 8.0}]})
    assert calm["overall_score"] == risky ["overall_score"]
    assert calm["risk_score"] != risky ["risk_score"]


def test_location_floor_blocks_the_top_band():
    from config import config
    from nodes.decision_node import decision_node

    def decide(location):
        return decision_node({
            "overall_score": config.strong_buy_score + 1, "risk_score": 0.0,
            "coordination_summary": {
                "component_scores": {"location": location},
                "annual_roi": config.min_roi * config.strong_roi_multiple + 1,
                "monthly_cash_flow": config.strong_cash_flow + 1}}) ["decision"]
                
    assert decide(config.location_threshold + 1) != decide (config.location_threshold - 2)


def test_roi_floor_blocks_the_buy_bands():
    from config import config
    from nodes.decision_node import decision_node

    def decide (roi):
        return decision_node({
            "overall_score": config.buy_score + 0.5, "risk_score": 0.0,
            "coordination_summary": {
                "component_scores": {"location": config.location_threshold + 1},
                "annual_roi": roi, "monthly_cash_flow": 0.0}}) ["decision"]

    assert decide (config.min_roi 1)! decide(config.min_roi 1)


def test_decision_preserves_the_unassessable_sentinel():
    from config import config
    from nodes.decision_node import decision_node
    strong_state = {
        "overall_score": config.strong_buy_score + 1, "risk_score": 0.0,
        "coordination_summary": {
            "component_scores": {"location": config.location_threshold + 1},
            "annual_roi": config.min_roi * config.strong_roi_multiple + 1,
            "monthly_cash_flow": config.strong_cash_flow + 1}}
    weak = decision_node({"overall_score": 0.0, "risk_score": 0.0, 
                            "coordination summary": {"component scores": {}}})["decision"]
    stuck = decision_node({**strong_state, "decision": weak})["decision"]
    assert stuck == weak
    assert stuck != decision_node(strong_state) ["decision"]
    
    
def test_decision_assigns_a_priority_and_risk_level():
    from config import config
    from nodes.decision_node import decision_node
    calm = decision_node({"overall_score": 0.0, "risk_score": 0.0,
                            "coordination_summary": {"component_scores": {}}})
    risky = decision_node({"overall_score": 0.0, "risk_score": config.high_risk + 1,
                            "coordination_summary": {"component_scores": {}}})
    assert calm["priority"] and calm ["risk_level"]
    assert calm["risk_level"] != risky ["risk_level"]
    

def test_coordinator_score_within_component_bounds():
    from nodes.coordinator_node import coordinator_node
    out = coordinator_node({
        "location_results": [{"location_score": 9.0}], "price_results": [{"pricing_score": 4.0}],
        "market_results": [{"market_score": 7.0}], "condition_results": [{"condition_score": 6.0}],
        "roi_results": [{"roi_score": 8.0, "risk_score": 3.0}],
    })
    components = list(out["coordination_summary"]["component_scores"].values())
    assert min(components) <= out ["overall_score"] <= max(components)
    assert 0.0 <= out ["overall_score"] <= 10.0
    

def test_coordinator_score_rises_with_components(): 
    from nodes.coordinator_node import coordinator_node

    def score_for(value):
        return coordinator_node({
            "location_results": [{"location_score": value}], "price_results": [{"pricing_score": value}],
            "market_results": [{"market_score": value}], "condition_results": [{"condition_score": value}],
            "roi_results": [{"roi_score": value, "risk_score": 0.0}],
        })["overall_score"]

    assert score_for(9.0) > score_for(2.0)
    assert score_for(0.0) <= score_for(5.0) <= score_for(10.0)


def test_coordinator_handles_missing_results():
    from nodes.coordinator_node import coordinator_node
    out = coordinator_node({"location_results": [], "price_results": [], "market_results": [],
                            "condition_results": [], "roi_results": []})
    assert 0.0 <= out["overall_score"] <= 10.0
    assert 0.0 <= out ["risk_score"] <= 10.0
    assert isinstance(out["coordination_summary"], dict) and out ["coordination_summary"]


def test_report_reflects_the_call_without_signoff():
    from nodes.report_node import report_node
    base = "ANY_DECISION"
    out = report_node({"analysis_id": "T", "decision": base, "human_decision": "",
                        "decision_metrics": {}, "coordination_summary": {}, "property": {}})
    assert base in str(out["report"])
    assert out.get("workflow_complete")        


def test_report_distinguishes_signoff_from_override():
    from nodes.report_node import report_node
    base = {"analysis_id": "T", "decision": "ANY_DECISION",
            "decision_metrics": {}, "coordination_summary": {}, "property": {}}
    approved = report_node ({**base, "human_decision": "approve"})
    overridden = report_node({**base, "human_decision": "override"})
    assert approved != overridden
    assert approved.get("workflow_complete") and overridden.get("workflow_complete")


def test_validation_files_an_incomplete_record_as_no_action():
    from nodes.validation_node import validation_node
    from nodes.decision_node import decision_node
    out = validation_node({"property": {"address": "Nowhere"}})
    assert isinstance(out.get("errors"), list) and out ["errors"]
    assert all(isinstance(entry, dict) for entry in out["errors"])
    weak = decision_node({"overall_score": 0.0, "risk_score": 0.0,
                            "coordination summary": {"component scores": {}}})["decision"]
    assert out.get("decision") == weak


def test_validation_passes_a_complete_record():
    import json
    from pathlib import Path
    from config import config
    from nodes.validation_node import validation_node
    record = json.loads(sorted (Path(config.data_dir).glob("*.json"))[0].read_text(encoding="utf-8"))
    out = validation_node({"property": record})
    assert not out.get("errors")
    assert out.get("decision") in (None, "")
    

def test_live_actionable_call_pauses (live_run):
    paused = live_run["paused"]
    assert paused.get("__interrupt__")
    payload = paused ["__interrupt__"][0].value
    assert isinstance(payload, dict) and len(payload) >= 2
    

def test_live_resume_completes(live_run):
    paused = live_run["paused"]
    final = live_run["final"]
    assert final.get("workflow_complete")
    assert paused ["decision"] in final ["report"]["decision"]
    