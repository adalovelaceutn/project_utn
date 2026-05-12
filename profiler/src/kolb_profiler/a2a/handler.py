"""A2A task handler — bridges JSON-RPC messages with the LangGraph agent."""
from __future__ import annotations

import re
from typing import Any

from langgraph.types import Command

from kolb_profiler.a2a.models import (
    Artifact,
    DataPart,
    Message,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)
from kolb_profiler.agent.state import InterviewState


def _extract_student_id(text: str) -> str | None:
    """Try to extract a student MongoDB ObjectId from a natural-language message."""
    match = re.search(r"[0-9a-f]{24}", text.lower())
    return match.group(0) if match else None


class A2AHandler:
    """Manages A2A task lifecycle on top of the compiled LangGraph."""

    def __init__(self, graph) -> None:
        self._graph = graph
        # In-memory task store: task_id → Task
        self._tasks: dict[str, Task] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def send(self, task_id: str, message: Message, metadata: dict[str, Any] | None = None) -> Task:
        """Create a new task or continue an existing one with a new message."""
        user_text = self._extract_text(message)
        metadata = metadata or {}

        if task_id not in self._tasks:
            return await self._start_task(task_id, user_text, metadata)
        try:
            return await self._continue_task(task_id, user_text, message)
        except KeyError as exc:
            # In rare cases the checkpointed graph state can be lost/corrupted
            # while the in-memory task still exists. Restarting avoids hard-failing
            # the whole /chat request with a 500.
            if str(exc) != "'history'":
                raise
            previous = self._tasks.get(task_id)
            recovered_metadata = dict(metadata)
            if previous is not None:
                recovered_metadata = {**previous.metadata, **recovered_metadata}
            self._tasks.pop(task_id, None)
            return await self._start_task(task_id, user_text, recovered_metadata)

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> Task | None:
        task = self._tasks.get(task_id)
        if task and task.status.state not in (TaskState.COMPLETED, TaskState.FAILED):
            task.status = TaskStatus(state=TaskState.CANCELED)
        return task

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(message: Message) -> str:
        for part in message.parts:
            if isinstance(part, TextPart):
                return part.text
        return ""

    def _config(self, task_id: str) -> dict:
        return {"configurable": {"thread_id": task_id}}

    async def _start_task(self, task_id: str, user_text: str, metadata: dict[str, Any]) -> Task:
        student_id = str(
            metadata.get("student_id")
            or metadata.get("user_id")
            or metadata.get("id")
            or _extract_student_id(user_text)
            or task_id
        ).strip()

        initial_state: InterviewState = {
            "student_id": student_id,
            "user_id": str(metadata.get("user_id") or metadata.get("student_id") or metadata.get("id") or student_id),
            "username": str(metadata.get("username") or metadata.get("user_name") or ""),
            "alumno_id": str(metadata.get("alumno_id") or student_id),
            "nombre": str(metadata.get("nombre") or metadata.get("username") or metadata.get("user_name") or ""),
            "email": str(metadata.get("email") or ""),
            "carrera": str(metadata.get("carrera") or ""),
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

        task = Task(
            id=task_id,
            status=TaskStatus(state=TaskState.WORKING),
            messages=[Message(role="user", parts=[TextPart(text=user_text)])],
            metadata=dict(metadata),
        )
        self._tasks[task_id] = task

        result = await self._graph.ainvoke(initial_state, self._config(task_id))
        return self._update_task_from_result(task_id, result)

    async def _continue_task(
        self, task_id: str, user_text: str, message: Message
    ) -> Task:
        task = self._tasks[task_id]
        task.messages.append(Message(role="user", parts=[TextPart(text=user_text)]))
        task.status = TaskStatus(state=TaskState.WORKING)

        result = await self._graph.ainvoke(
            Command(resume=user_text), self._config(task_id)
        )
        return self._update_task_from_result(task_id, result)

    def _update_task_from_result(self, task_id: str, result: dict) -> Task:
        task = self._tasks[task_id]

        # Check whether the graph is still interrupted (waiting for input)
        graph_state = self._graph.get_state(self._config(task_id))
        still_interrupted = bool(
            graph_state.tasks
            and any(t.interrupts for t in graph_state.tasks)
        )

        if still_interrupted:
            # Extract the question from the interrupt payload
            question = result.get("current_question", "")
            if not question:
                # Try to get from interrupt value
                for t in graph_state.tasks:
                    for intr in t.interrupts:
                        if isinstance(intr.value, dict):
                            question = intr.value.get("question", "")

            task.status = TaskStatus(state=TaskState.INPUT_REQUIRED)
            task.messages.append(
                Message(role="agent", parts=[TextPart(text=question)])
            )
        else:
            # Graph is done
            kolb_profile = result.get("kolb_profile")
            if kolb_profile:
                farewell = result.get("current_question", "")
                if farewell:
                    task.messages.append(
                        Message(role="agent", parts=[TextPart(text=farewell)])
                    )
                task.artifacts.append(
                    Artifact(
                        name="kolb_profile",
                        description="Perfil de estilos de aprendizaje Kolb del estudiante",
                        parts=[DataPart(data=kolb_profile)],
                    )
                )
                task.status = TaskStatus(state=TaskState.COMPLETED)
                task.metadata["persisted_profile_id"] = result.get(
                    "persisted_profile_id"
                )
            else:
                error = result.get("error", "Error desconocido")
                task.status = TaskStatus(state=TaskState.FAILED, message=error)

        return task
