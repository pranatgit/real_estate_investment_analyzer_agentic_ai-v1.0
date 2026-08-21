"""Streamlit presentation layer for the Investment Desk."""

import html
import json
from pathlib import Path

import streamlit as st

from config import config


PROPERTY_TYPES = ["single_family", "multi_family", "condo", "townhouse"]
CONDITIONS = ["excellent", "good", "fair", "poor"]
SCHOOLS = ["excellent", "great", "good", "average", "below_average", "poor"]
CRIME = ["very_safe", "safe", "moderate", "concerning", "high_crime"]


def _pretty(value: str) -> str:
    return str(value or "-").replace("_", " ").title()


def _money(value) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "-"


def _render_property_preview(record: dict) -> None:
    st.subheader(str(record.get("address", "")))
    st.caption(f"{record.get('city', '')}, {record.get('state', '')}")
    cols = st.columns(5)
    cols[0].metric("Asking", _money(record.get("listing_price", 0)))
    cols[1].metric("Size", f"{record.get('square_footage', 0)} sqft")
    cols[2].metric("Built", str(record.get("year_built", "")))
    cols[3].metric("Rent", f"{_money(record.get('estimated_rent', 0))}/mo")
    cols[4].metric("Comps", str(len(record.get("comparable_properties", []))))

    st.write(
        f"**Type:** {_pretty(record.get('property_type'))} · "
        f"**Beds/Baths:** {record.get('bedrooms', 0)}/{record.get('bathrooms', 0)} · "
        f"**Condition:** {_pretty(record.get('overall_condition'))}"
    )
    st.write(
        f"**Schools:** {_pretty(record.get('school_rating'))} · "
        f"**Crime:** {_pretty(record.get('crime_rating'))} · "
        f"**Walk:** {record.get('walkability_score', 0)}"
    )


def _collect_property(mode: str) -> dict:
    if mode == "Sample":
        records = {
            p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(Path(config.data_dir).glob("*.json"))
        }
        if not records:
            return {}
        chosen = st.selectbox("Sample property", list(records))
        record = records[chosen]
        _render_property_preview(record)
        return record

    left, right = st.columns(2)
    with left:
        address = st.text_input("Address", "45 Alder Street")
        city = st.text_input("City", "Denver")
        state_code = st.text_input("State", "CO")
        property_type = st.selectbox("Type", PROPERTY_TYPES)
        listing_price = st.number_input("Asking price", 10000, 10000000, 400000, step=5000)
        square_footage = st.number_input("Square footage", 200, 20000, 1800, step=50)
        year_built = st.number_input("Year built", 1850, 2026, 2008)
        overall_condition = st.selectbox("Condition", CONDITIONS, index=1)
    with right:
        school_rating = st.selectbox("Schools", SCHOOLS, index=2)
        crime_rating = st.selectbox("Crime", CRIME, index=1)
        walkability_score = st.slider("Walk score", 0, 100, 60)
        transit_score = st.slider("Transit score", 0, 100, 45)
        estimated_rent = st.number_input("Estimated rent / mo", 200, 50000, 2600, step=50)
        interest_rate = st.number_input("Interest rate %", 0.0, 20.0, 7.0, step=0.25)
        property_tax_annual = st.number_input("Property tax / yr", 0, 100000, 5000, step=100)
        hoa_monthly = st.number_input("HOA / mo", 0, 5000, 0, step=25)
        maintenance_annual = st.number_input("Maintenance / yr", 0, 100000, 2000, step=100)

    if not address.strip():
        return {}

    record = {
        "address": address,
        "city": city,
        "state": state_code,
        "zip_code": "",
        "property_type": property_type,
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_footage": int(square_footage),
        "year_built": int(year_built),
        "listing_price": int(listing_price),
        "comparable_properties": [],
        "school_rating": school_rating,
        "crime_rating": crime_rating,
        "walkability_score": int(walkability_score),
        "transit_score": int(transit_score),
        "amenities": [],
        "commute_time_minutes": 30,
        "overall_condition": overall_condition,
        "component_conditions": {},
        "recent_updates": [],
        "known_issues": [],
        "historical_prices": [],
        "avg_days_on_market": 45,
        "current_inventory": 100,
        "price_reductions": 15.0,
        "estimated_rent": int(estimated_rent),
        "down_payment_percent": 20,
        "interest_rate": float(interest_rate),
        "property_tax_annual": int(property_tax_annual),
        "insurance_annual": 1200,
        "hoa_monthly": int(hoa_monthly),
        "maintenance_annual": int(maintenance_annual),
    }
    _render_property_preview(record)
    return record


def render_metrics(metrics: dict) -> None:
    components = metrics.get("component_scores", {})
    cols = st.columns(6)
    values = [
        ("Overall", metrics.get("overall_score", 0)),
        ("Location", components.get("location", 0)),
        ("Price", components.get("price", 0)),
        ("Market", components.get("market", 0)),
        ("Condition", components.get("condition", 0)),
        ("ROI", components.get("roi", 0)),
    ]
    for col, (label, value) in zip(cols, values):
        col.metric(label, f"{float(value):.1f}/10")


def render_outcome(values: dict) -> None:
    report = values.get("report") or {}
    st.subheader("Financials")
    cols = st.columns(4)
    cols[0].metric("Annual ROI", f"{float(report.get('annual_roi', 0)):.1f}%")
    cols[1].metric("Cash Flow", f"{_money(report.get('monthly_cash_flow', 0))}/mo")
    cols[2].metric("Cap Rate", f"{float(report.get('cap_rate', 0)):.1f}%")
    cols[3].metric("Risk", f"{float(report.get('risk_score', 0)):.1f}/10")

    st.subheader("Assessment")
    st.write(
        f"Location: **{report.get('location_tier', '-') }** · "
        f"Price: **{report.get('price_verdict', '-') }** · "
        f"Market: **{report.get('market_temperature', '-') }** · "
        f"Condition: **{report.get('condition_tier', '-') }**"
    )

    for title, key in [
        ("Key findings", "key_findings"),
        ("Risk factors", "risk_factors"),
        ("Negotiation points", "negotiation_points"),
        ("Action items", "action_items"),
    ]:
        items = report.get(key) or []
        if items:
            st.subheader(title)
            for item in items[:8]:
                st.markdown(f"- {html.escape(str(item))}")


def render_app(run_analysis, approve_decision, override_decision, recent_analyses) -> None:
    st.set_page_config(page_title="Investment Desk", layout="wide")
    st.title("Investment Desk")
    st.caption("Four parallel analyses → ROI and independent risk → governed investment call → analyst sign-off.")

    with st.sidebar:
        st.subheader("Recent analyses")
        history = recent_analyses(10)
        if not history:
            st.caption("No analyses yet.")
        for row in history:
            st.write(
                f"**{row.get('address') or row.get('analysis_id')}**  \n"
                f"{_pretty(row.get('decision'))} · {row.get('city', '')} · "
                f"{float(row.get('overall_score', 0)):.1f}/10"
            )

    st.subheader("New analysis")
    mode = st.radio("Input source", ["Sample", "Custom"], horizontal=True)
    record = _collect_property(mode)

    if st.button("Analyse property", type="primary"):
        if record:
            with st.spinner("Running the investment analyses..."):
                st.session_state["result"] = run_analysis(record)
        else:
            st.warning("Choose a sample property, or enter an address.")

    result = st.session_state.get("result")
    if not result:
        return

    values = result["values"]

    if values.get("errors"):
        st.error(
            "Analysis errors: "
            + " | ".join(str(e.get("error", "")) for e in values["errors"][:4])
        )

    if result.get("interrupted"):
        payload = result["interrupt_payload"]
        st.subheader("Recommendation")
        st.warning(
            f"{payload.get('decision')} · {payload.get('priority')} · "
            f"{payload.get('risk_level')}. {payload.get('question')}"
        )
        render_metrics(payload.get("metrics", {}))

        approve_col, override_col = st.columns(2)
        if approve_col.button("Sign off", type="primary", use_container_width=True):
            resumed = approve_decision(result["thread_id"])
            st.session_state["result"] = {
                "values": resumed,
                "interrupted": False,
                "thread_id": result["thread_id"],
            }
            st.rerun()

        if override_col.button("Override", use_container_width=True):
            resumed = override_decision(result["thread_id"])
            st.session_state["result"] = {
                "values": resumed,
                "interrupted": False,
                "thread_id": result["thread_id"],
            }
            st.rerun()
        return

    report = values.get("report") or {}
    st.subheader("Outcome")
    st.success(
        f"{report.get('decision', values.get('decision', ''))} · "
        f"Priority: {report.get('priority', '')} · Risk: {report.get('risk_level', '')}"
    )
    render_metrics(report.get("decision_metrics", values.get("decision_metrics", {})))
    render_outcome(values)
