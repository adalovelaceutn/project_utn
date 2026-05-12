from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from kolb_profiler.agent.nodes import make_nodes
from kolb_profiler.agent.state import InterviewState
from kolb_profiler.clients.mcp import KolbMCPClient
from kolb_profiler.clients.profiler_api import ProfilerAPIClient


def build_graph(mcp_client: KolbMCPClient, api_client: ProfilerAPIClient, llm):
    """Return a compiled LangGraph graph with MemorySaver checkpointing.

    Flow
    ----
    START → get_scenario → format_question → process_response
              ↑ (loop back if < 12)                 ↓
              └─────────────────────────── check_done_router
                                                     ↓ (== 12)
                                                  finalize → END

    The ``process_response`` node calls ``interrupt()`` internally, which
    pauses execution until the A2A caller provides the student's answer via
    ``Command(resume=<answer>)``.
    """
    nodes = make_nodes(mcp_client, api_client, llm)

    builder = StateGraph(InterviewState)

    builder.add_node("get_scenario", nodes["get_scenario"])
    builder.add_node("format_question", nodes["format_question"])
    builder.add_node("process_response", nodes["process_response"])
    builder.add_node("finalize", nodes["finalize"])

    builder.add_edge(START, "get_scenario")
    builder.add_edge("get_scenario", "format_question")
    builder.add_edge("format_question", "process_response")
    builder.add_conditional_edges(
        "process_response",
        nodes["check_done_router"],
        {
            "get_scenario": "get_scenario",
            "finalize": "finalize",
        },
    )
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=MemorySaver())
