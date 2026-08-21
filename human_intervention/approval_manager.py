"""Resume paused analyst reviews."""

from typing import Any, Dict

from langgraph.types import Command


def _resume(compiled_graph, thread_id: str, action: str) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    return compiled_graph.invoke(Command(resume={"action": action}), config=config)


def approve_analysis(compiled_graph, thread_id: str) -> Dict[str, Any]:
    return _resume(compiled_graph, thread_id, "approve")


def override_analysis(compiled_graph, thread_id: str) -> Dict[str, Any]:
    return _resume(compiled_graph, thread_id, "override")
