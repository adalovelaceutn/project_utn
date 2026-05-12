"""Smoke-tests for the LangGraph interview graph."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage

from kolb_profiler.agent.graph import build_graph
from kolb_profiler.agent.nodes import _calculate_profile, _detect_option


# ---------------------------------------------------------------------------
# Unit: _detect_option
# ---------------------------------------------------------------------------

FAKE_SCENARIO = {
    "id": 1,
    "titulo": "Test",
    "contexto": "ctx",
    "opciones": [
        {"id": "A", "texto": "Opción A", "dimension": "EC"},
        {"id": "B", "texto": "Opción B", "dimension": "OR"},
        {"id": "C", "texto": "Opción C", "dimension": "CA"},
    ],
}


def test_detect_option_exact():
    oid, dim = _detect_option("A", FAKE_SCENARIO)
    assert oid == "A"
    assert dim == "EC"


def test_detect_option_prefix():
    oid, dim = _detect_option("B. Me gusta reflexionar", FAKE_SCENARIO)
    assert oid == "B"
    assert dim == "OR"


def test_detect_option_freetext():
    oid, dim = _detect_option("Prefiero hacer cosas prácticas", FAKE_SCENARIO)
    assert oid is None
    assert dim is None


# ---------------------------------------------------------------------------
# Unit: _calculate_profile
# ---------------------------------------------------------------------------

def _make_history(dims: list[str]) -> list[dict]:
    return [
        {"scenario_id": i, "scenario_title": f"S{i}", "option_id": "A",
         "dimension": d, "raw_response": "resp"}
        for i, d in enumerate(dims, 1)
    ]


def test_calculate_profile_convergente():
    # CA > EC, EA > OR → Convergente
    history = _make_history(["CA"] * 4 + ["EA"] * 4 + ["OR"] * 2 + ["EC"] * 2)
    profile = _calculate_profile("abc123", history)
    assert profile["predominant_style"] == "Convergente"
    assert profile["student_id"] == "abc123"
    assert 0 <= profile["confidence_score"] <= 1


def test_calculate_profile_divergente():
    # EC > CA, OR > EA → Divergente
    history = _make_history(["EC"] * 4 + ["OR"] * 4 + ["CA"] * 2 + ["EA"] * 2)
    profile = _calculate_profile("abc123", history)
    assert profile["predominant_style"] == "Divergente"


def test_calculate_profile_axis_mapping():
    history = _make_history(["EC"] * 3 + ["OR"] * 3 + ["CA"] * 3 + ["EA"] * 3)
    profile = _calculate_profile("abc123", history)
    assert profile["axis_scores"]["CE"] == 3
    assert profile["axis_scores"]["RO"] == 3
    assert profile["axis_scores"]["AC"] == 3
    assert profile["axis_scores"]["AE"] == 3
    assert profile["puntajes"]["experiencia_concreta"] == 25


# ---------------------------------------------------------------------------
# Integration smoke: graph builds and starts without errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_starts_and_interrupts():
    """Verify the graph starts, fetches first scenario and interrupts."""
    # Mock MCP client: returns scenario 1
    mcp_mock = AsyncMock()
    mcp_mock.next_scenario.return_value = {
        "scenario": {
            "id": 1,
            "titulo": "Proyecto en equipo",
            "contexto": "Tu equipo debe resolver un reto...",
            "opciones": [
                {"id": "A", "texto": "Observo", "dimension": "OR"},
                {"id": "B", "texto": "Teorizo", "dimension": "CA"},
                {"id": "C", "texto": "Actúo", "dimension": "EA"},
            ],
        },
        "position": 1,
        "remaining": 11,
        "partial_scores": {},
    }

    # Mock API client
    api_mock = AsyncMock()
    api_mock.create_profile.return_value = "6630000000000000deadbeef"

    # Mock LLM
    llm_mock = AsyncMock()
    llm_mock.ainvoke.return_value = AIMessage(content="Pregunta formateada de prueba")

    graph = build_graph(mcp_mock, api_mock, llm_mock)

    from kolb_profiler.agent.state import InterviewState

    initial: InterviewState = {
        "dni": "18447836",
        "history": [],
        "current_scenario": None,
        "current_question": None,
        "position": 0,
        "remaining": 12,
        "partial_scores": {},
        "messages": [],
        "kolb_profile": None,
        "persisted_profile_id": None,
        "error": None,
    }

    config = {"configurable": {"thread_id": "test-thread-1"}}

    result = await graph.ainvoke(initial, config)
    assert result is not None

    state = graph.get_state(config)
    assert state is not None
    assert state.tasks
    assert any(t.interrupts for t in state.tasks)
