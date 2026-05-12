from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, Field


class ChatUserContext(BaseModel):
    id: str = Field(validation_alias=AliasChoices("id", "user_id", "student_id"))
    username: str = Field(validation_alias=AliasChoices("username", "user_name"))
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None
    dni: str | None = None

    def to_profiler_metadata(self) -> dict[str, str]:
        return {
            "username": self.username,
            "user_name": self.username,
            "dni": (self.dni or "").strip(),
        }


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    user: ChatUserContext


class ChatResponse(BaseModel):
    session_id: str
    task_id: str
    state: str
    reply: str
    profile: dict[str, Any] | None = None
    persisted_profile_id: str | None = None