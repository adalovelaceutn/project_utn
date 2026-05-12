from __future__ import annotations

import json
import math
import re
from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt

from kolb_profiler.agent.prompts import (
    CLASSIFY_TEMPLATE,
    FAREWELL_TEMPLATE,
    INTERVIEW_SYSTEM,
    SCENARIO_TEMPLATE,
)
from kolb_profiler.agent.state import InterviewState
from kolb_profiler.clients.mcp import KolbMCPClient
from kolb_profiler.clients.profiler_api import ProfilerAPIClient

_VALID_DIMS = {"EC", "OR", "CA", "EA"}
_TOTAL_SCENARIOS = 12


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_options(opciones: list[dict]) -> str:
    return "\n".join(f"  {o['id']}) {o['texto']}" for o in opciones)


def _detect_option(text: str, scenario: dict) -> tuple[str | None, str | None]:
    """Return (option_id, dimension) if the student picked A, B or C directly."""
    t = text.strip().upper()
    for opt in scenario["opciones"]:
        oid = opt["id"]
        if t == oid or t.startswith(oid + " ") or t.startswith(oid + ".") or t.startswith(oid + ")"):
            return opt["id"], opt["dimension"]
    return None, None


async def _classify_with_llm(scenario: dict, response: str, llm) -> str:
    """Use the LLM to classify a free-text response into a Kolb dimension."""
    prompt = CLASSIFY_TEMPLATE.format(
        scenario_title=scenario["titulo"],
        scenario_context=scenario["contexto"],
        student_response=response,
    )
    result = await llm.ainvoke([HumanMessage(content=prompt)])
    raw = result.content.strip()

    # Try JSON parse first
    try:
        data = json.loads(raw)
        dim = str(data.get("dimension", "")).upper()
        if dim in _VALID_DIMS:
            return dim
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: regex search
    match = re.search(r"\b(EC|OR|CA|EA)\b", raw.upper())
    return match.group(1) if match else "OR"  # default fallback


def _calculate_profile(student_id: str, history: list[dict]) -> dict:
    """Compute the Kolb profile dict ready to POST to the API."""
    scores = {d: 0 for d in _VALID_DIMS}
    interview_items = []

    for entry in history:
        dim = entry.get("dimension")
        if dim in scores:
            scores[dim] += 1
        interview_items.append({
            "scenario": entry.get("scenario_title", ""),
            "response": entry.get("raw_response", ""),
            "classification": dim or "unknown",
        })

    # Axes (Kolb standard)
    y = scores["CA"] - scores["EC"]   # AC - CE
    x = scores["EA"] - scores["OR"]   # AE - RO

    # Quadrant
    if y >= 0 and x >= 0:
        style = "Convergente"
    elif y >= 0 and x < 0:
        style = "Asimilador"
    elif y < 0 and x >= 0:
        style = "Acomodador"
    else:
        style = "Divergente"

    # Confidence: normalized distance from origin
    n = len(history) or 1
    distance = math.sqrt(x ** 2 + y ** 2)
    max_d = math.sqrt(2) * n
    confidence = round(min(distance / max_d, 1.0), 2)

    return {
        "id_student": student_id,
        "last_evaluation_date": date.today().isoformat(),
        "predominant_style": style,
        "confidence_score": confidence,
        "axis_scores": {
            "CE": scores["EC"],
            "RO": scores["OR"],
            "AC": scores["CA"],
            "AE": scores["EA"],
        },
        "interview": interview_items,
        "evidence": [],
    }


# ---------------------------------------------------------------------------
# Node factories — closures capture mcp_client, api_client, llm
# ---------------------------------------------------------------------------

def make_nodes(mcp_client: KolbMCPClient, api_client: ProfilerAPIClient, llm):

    async def get_scenario_node(state: InterviewState) -> dict:
        """Fetch the next scenario from the MCP server."""
        result = await mcp_client.next_scenario(state["history"])
        if result is None:
            return {}   # should not happen; graph routing handles 12-done
        return {
            "current_scenario": result["scenario"],
            "position": result["position"],
            "remaining": result["remaining"],
            "partial_scores": result["partial_scores"],
        }

    async def format_question_node(state: InterviewState) -> dict:
        """Use the LLM to present the scenario conversationally."""
        scenario = state["current_scenario"]
        prompt = SCENARIO_TEMPLATE.format(
            position=state["position"],
            titulo=scenario["titulo"],
            contexto=scenario["contexto"],
            opciones=_format_options(scenario["opciones"]),
        )
        response = await llm.ainvoke(
            [SystemMessage(content=INTERVIEW_SYSTEM), HumanMessage(content=prompt)]
        )
        return {
            "current_question": response.content,
            "messages": [response],
        }

    async def process_response_node(state: InterviewState) -> dict:
        """Interrupt to get the student's answer, then classify it."""
        # Pause graph — A2A caller receives current_question and resumes with the student's text
        student_input: str = interrupt({"question": state["current_question"]})

        scenario = state["current_scenario"]
        option_id, dimension = _detect_option(student_input, scenario)

        if dimension is None:
            # Free-text response: use LLM sampling to classify
            dimension = await _classify_with_llm(scenario, student_input, llm)
            option_id = "free"

        entry = {
            "scenario_id": scenario["id"],
            "scenario_title": scenario["titulo"],
            "option_id": option_id,
            "dimension": dimension,
            "raw_response": student_input,
        }

        updated_history = state["history"] + [entry]
        updated_scores = {**state.get("partial_scores", {})}
        updated_scores[dimension] = updated_scores.get(dimension, 0) + 1

        return {
            "history": updated_history,
            "partial_scores": updated_scores,
        }

    async def finalize_node(state: InterviewState) -> dict:
        """Calculate the Kolb profile, persist it, and generate a farewell."""
        profile = _calculate_profile(state["student_id"], state["history"])

        persisted_id: str | None = None
        error: str | None = None
        try:
            persisted_id = await api_client.create_profile(profile)
        except Exception as exc:
            error = f"API persist failed: {exc}"

        # Farewell message via LLM
        farewell = await llm.ainvoke(
            [SystemMessage(content=INTERVIEW_SYSTEM), HumanMessage(content=FAREWELL_TEMPLATE)]
        )

        return {
            "kolb_profile": profile,
            "persisted_profile_id": persisted_id,
            "error": error,
            "current_question": farewell.content,
            "messages": [farewell],
        }

    def check_done_router(state: InterviewState) -> str:
        if len(state.get("history", [])) >= _TOTAL_SCENARIOS:
            return "finalize"
        return "get_scenario"

    return {
        "get_scenario": get_scenario_node,
        "format_question": format_question_node,
        "process_response": process_response_node,
        "finalize": finalize_node,
        "check_done_router": check_done_router,
    }
