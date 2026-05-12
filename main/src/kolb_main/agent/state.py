from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class MainAgentState(TypedDict):
    session_id: str
    task_id: str | None
    incoming_message: str
    user_context: dict[str, Any]
    profiler_metadata: dict[str, str]
    a2a_task: dict[str, Any] | None
    reply: str | None
    state: str | None
    profile: dict[str, Any] | None
    persisted_profile_id: str | None