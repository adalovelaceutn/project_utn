from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage


BLOCKED_REPLY = (
    "Perdon, solo puedo conversar sobre pedagogia relacionada con tu perfil KOLB "
    "o sobre el modelo de aprendizaje KOLB."
)

_KOLB_KEYWORDS = (
    "kolb",
    "aprendizaje",
    "estilo",
    "pedagog",
    "ensen",
    "didactic",
    "evaluacion",
    "docencia",
    "aula",
    "estudiante",
    "perfil",
    "convergente",
    "divergente",
    "asimilador",
    "acomodador",
)


def _heuristic_topic_match(message: str) -> bool:
    lowered = message.lower()
    return any(token in lowered for token in _KOLB_KEYWORDS)


def _extract_text(result: Any) -> str:
    content = getattr(result, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                chunks.append(item["text"])
        return "\n".join(chunks).strip()
    return str(content).strip()


async def is_topic_allowed(message: str, profile: dict[str, Any], llm: Any | None) -> bool:
    """True only when the user message is about Kolb pedagogy/profile topics."""
    if _heuristic_topic_match(message):
        return True

    if llm is None:
        return False

    system_prompt = (
        "Clasifica si el mensaje del estudiante ESTA DENTRO o FUERA de alcance. "
        "Dentro de alcance: pedagogia relacionada con su perfil KOLB o dudas sobre el modelo de aprendizaje KOLB. "
        "Fuera de alcance: cualquier otro tema (programacion general, deportes, politica, entretenimiento, etc.). "
        "Responde solo una palabra: ALLOW o BLOCK."
    )
    user_prompt = (
        f"Perfil disponible: {profile}\n"
        f"Mensaje: {message}"
    )

    try:
        result = await llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
    except Exception:
        return False

    normalized = _extract_text(result).upper()
    if "ALLOW" in normalized and "BLOCK" not in normalized:
        return True
    return False
