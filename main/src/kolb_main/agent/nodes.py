from __future__ import annotations

from typing import Any

from kolb_main.clients.profiler_a2a import ProfilerA2AClient
from kolb_main.models import ChatUserContext


def _extract_last_agent_text(task: dict[str, Any]) -> str:
    messages = task.get("messages", [])
    for message in reversed(messages):
        if message.get("role") != "agent":
            continue
        for part in message.get("parts", []):
            if part.get("type") == "text":
                return str(part.get("text", "")).strip()
    status = task.get("status", {})
    return str(status.get("message") or "No hubo respuesta del agente.")


def _extract_profile(task: dict[str, Any]) -> dict[str, Any] | None:
    for artifact in reversed(task.get("artifacts", [])):
        if artifact.get("name") != "kolb_profile":
            continue
        for part in artifact.get("parts", []):
            if part.get("type") == "data":
                return part.get("data")
    return None


def make_nodes(client: ProfilerA2AClient):
    async def prepare_context_node(state: dict[str, Any]) -> dict[str, Any]:
        user = ChatUserContext(**state["user_context"])
        return {
            "task_id": state.get("task_id") or state["session_id"],
            "profiler_metadata": user.to_profiler_metadata(),
        }

    async def delegate_to_profiler_node(state: dict[str, Any]) -> dict[str, Any]:
        task = await client.send_task(
            task_id=state["task_id"],
            text=state["incoming_message"],
            metadata=state["profiler_metadata"],
        )
        return {"a2a_task": task}

    async def normalize_response_node(state: dict[str, Any]) -> dict[str, Any]:
        task = state["a2a_task"] or {}
        profile = _extract_profile(task)
        return {
            "reply": _extract_last_agent_text(task),
            "state": task.get("status", {}).get("state", "failed"),
            "profile": profile,
            "persisted_profile_id": task.get("metadata", {}).get("persisted_profile_id"),
        }

    return {
        "prepare_context": prepare_context_node,
        "delegate_to_profiler": delegate_to_profiler_node,
        "normalize_response": normalize_response_node,
    }