"""Validate the property record without raising on missing required fields."""

from typing import Any, Dict

from config import REQUIRED_FIELDS


def validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    record = state.get("property") or {}
    missing = [field for field in REQUIRED_FIELDS if field not in record or record.get(field) in (None, "")]
    if not missing:
        return {}

    return {
        "errors": [
            {
                "node": "validate",
                "error": f"Missing required field: {field}",
            }
            for field in missing
        ],
        # PASS is the assignment's no-action sentinel for an unassessable record.
        "decision": "PASS",
    }
