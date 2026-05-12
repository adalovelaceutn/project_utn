from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from kolb_main.agent.nodes import make_nodes
from kolb_main.agent.state import MainAgentState
from kolb_main.clients.profiler_a2a import ProfilerA2AClient


def build_graph(client: ProfilerA2AClient):
    nodes = make_nodes(client)

    builder = StateGraph(MainAgentState)
    builder.add_node("prepare_context", nodes["prepare_context"])
    builder.add_node("delegate_to_profiler", nodes["delegate_to_profiler"])
    builder.add_node("normalize_response", nodes["normalize_response"])

    builder.add_edge(START, "prepare_context")
    builder.add_edge("prepare_context", "delegate_to_profiler")
    builder.add_edge("delegate_to_profiler", "normalize_response")
    builder.add_edge("normalize_response", END)

    return builder.compile(checkpointer=MemorySaver())