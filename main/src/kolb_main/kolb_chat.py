from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from kolb_main.clients.mcp_client import MainMCPClient
from kolb_main.clients.tavily_client import TavilyClient


def _normalize_style(profile: dict[str, Any]) -> str:
    style = str(profile.get("predominant_style") or "").strip()
    if style:
        return style

    puntajes = profile.get("puntajes") or {}
    ce = int(puntajes.get("experiencia_concreta") or 0)
    ro = int(puntajes.get("observacion_reflexiva") or 0)
    ac = int(puntajes.get("conceptualizacion_abstracta") or 0)
    ae = int(puntajes.get("experimentacion_activa") or 0)

    y = ac - ce
    x = ae - ro
    if y >= 0 and x >= 0:
        return "Convergente"
    if y >= 0 and x < 0:
        return "Asimilador"
    if y < 0 and x >= 0:
        return "Acomodador"
    return "Divergente"


def _format_sources(results: list[dict[str, Any]]) -> str:
    if not results:
        return "Sin fuentes externas."
    lines: list[str] = []
    for idx, item in enumerate(results, start=1):
        title = item.get("title") or "Sin titulo"
        url = item.get("url") or ""
        content = item.get("content") or ""
        lines.append(f"{idx}. {title} | {url}\n{content[:450]}")
    return "\n\n".join(lines)


async def build_profile_chat_reply(
    *,
    message: str,
    profile: dict[str, Any],
    mcp_client: MainMCPClient,
    llm: Any | None,
    tavily_client: TavilyClient | None,
) -> str:
    """Build a pedagogical reply for users that already have a Kolb profile."""
    style = _normalize_style(profile)

    try:
        theory = await mcp_client.get_profile_theory(style)
    except Exception:
        theory = {
            "nombre": style,
            "descripcion_modelo": "El modelo de Kolb describe un ciclo entre sentir, pensar, observar y hacer.",
            "descripcion": "",
            "estrategia_agente": "",
            "formula": "",
        }

    web_context: list[dict[str, Any]] = []
    if tavily_client is not None and tavily_client.enabled:
        try:
            web_context = await tavily_client.search(
                query=f"Modelo de aprendizaje Kolb pedagogia {message}",
                max_results=3,
            )
        except Exception:
            web_context = []

    if llm is None:
        return (
            f"Segun el modelo de Kolb, aprender implica un ciclo entre sentir, observar, pensar y hacer. "
            f"En tu caso, el estilo predominante es {theory.get('nombre', style)} ({theory.get('formula', 'sin formula')}). "
            f"Descripcion: {theory.get('descripcion', 'Sin descripcion disponible')}. "
            f"Recomendacion pedagogica: {theory.get('estrategia_agente', 'Combinar reflexion y practica guiada.')}"
        )

    system_prompt = (
        "Eres un asistente de pedagogia especializado en el modelo de aprendizaje KOLB. "
        "El estudiante YA TIENE perfil KOLB. Nunca inicies ni continúes una entrevista, "
        "nunca hagas preguntas de relevamiento, y nunca pidas responder escenarios. "
        "Debes responder en formato explicativo y accionable, centrado en el perfil y en el modelo Kolb. "
        "Si hay fuentes externas, utilízalas solo como apoyo y no inventes citas. "
        "Responde en espanol, claro y breve."
    )

    user_prompt = (
        f"Consulta del estudiante: {message}\n\n"
        f"Perfil Kolb del estudiante: {profile}\n\n"
        f"Marco teorico Kolb para su estilo: {theory}\n\n"
        f"Fuentes externas (Tavily):\n{_format_sources(web_context)}"
    )

    result = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    content = getattr(result, "content", "")
    if isinstance(content, str):
        return content.strip() or "No pude generar una respuesta en este momento."
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                chunks.append(item["text"])
        joined = "\n".join(chunks).strip()
        return joined or "No pude generar una respuesta en este momento."
    return str(content).strip() or "No pude generar una respuesta en este momento."
