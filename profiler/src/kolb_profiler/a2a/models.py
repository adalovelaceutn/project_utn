"""A2A (Agent-to-Agent) protocol models — simplified Google A2A spec."""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TextPart(BaseModel):
    type: str = "text"
    text: str


class DataPart(BaseModel):
    type: str = "data"
    data: dict[str, Any]


class Message(BaseModel):
    role: str                          # "user" | "agent"
    parts: list[TextPart | DataPart]


class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[str] = None


class Artifact(BaseModel):
    name: str
    description: Optional[str] = None
    parts: list[TextPart | DataPart]


class Task(BaseModel):
    id: str
    status: TaskStatus
    messages: list[Message] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# JSON-RPC envelope
# ---------------------------------------------------------------------------

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# tasks/send params
# ---------------------------------------------------------------------------

class SendTaskParams(BaseModel):
    id: str                             # task ID (client-generated)
    message: Message                    # new message from the orchestrator
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Agent card (discovery)
# ---------------------------------------------------------------------------

AGENT_CARD = {
    "name": "Kolb Profiler Agent",
    "description": (
        "Conducts a 12-scenario Kolb learning-style interview with a student "
        "and persists the resulting profile to the IA-Agents API."
    ),
    "url": "http://localhost:8001",
    "version": "0.1.0",
    "documentationUrl": None,
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
    },
    "skills": [
        {
            "id": "kolb-interview",
            "name": "Kolb Learning Style Interview",
            "description": (
                "Runs a 12-scenario adaptive interview, classifies each response "
                "into EC/OR/CA/EA dimensions, calculates the Kolb quadrant profile, "
                "and persists it via the profiler API."
            ),
            "tags": ["education", "learning-styles", "kolb", "psychopedagogy"],
            "inputModes": ["text"],
            "outputModes": ["text", "data"],
            "examples": [
                "Iniciar entrevista para el estudiante con id: <student_id>",
            ],
        }
    ],
}
