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
    carrera: str | None = None

    def to_profiler_metadata(self) -> dict[str, str]:
        full_name = " ".join(part for part in [self.nombre, self.apellido] if part).strip()
        return {
            "student_id": self.id,
            "user_id": self.id,
            "username": self.username,
            "user_name": self.username,
            "id": self.id,
            "alumno_id": (self.dni or self.id),
            "nombre": full_name or self.username,
            "email": self.email or "sin-informar@example.com",
            "carrera": self.carrera or "Sin informar",
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