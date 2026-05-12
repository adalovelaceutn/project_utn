from __future__ import annotations

import json
import re

from mcp.server.fastmcp import Context
from mcp.types import SamplingMessage, TextContent


_SYSTEM_PROMPT = """\
Eres un experto en psicopedagogía del modelo de estilos de aprendizaje de Kolb.
Tu única tarea es clasificar la intención de una respuesta de un estudiante
en exactamente UNO de los cuatro pilares de Kolb:

- EC  (Experiencia Concreta):       sentir, vivenciar, conectar emocionalmente.
- OR  (Observación Reflexiva):       observar, reflexionar, escuchar, analizar perspectivas.
- CA  (Conceptualización Abstracta): pensar, teorizar, sistematizar, deducir con lógica.
- EA  (Experimentación Activa):      hacer, actuar, aplicar, probar, tomar decisiones.

Responde ÚNICAMENTE con un objeto JSON válido con dos claves:
  "dimension": uno de ["EC", "OR", "CA", "EA"]
  "confidence": número entre 0.0 y 1.0

No incluyas explicación ni texto adicional fuera del JSON.
"""

_USER_TEMPLATE = """\
Escenario: {scenario_title}
Contexto del escenario: {scenario_context}
Respuesta del estudiante: {student_response}
"""

_VALID_DIMENSIONS = {"EC", "OR", "CA", "EA"}


def _parse_dimension_result(text: str) -> dict:
    """Extrae dimension y confidence del texto JSON devuelto por el LLM."""
    # Intentar parsear JSON directo
    try:
        data = json.loads(text.strip())
        dim = str(data.get("dimension", "")).upper()
        conf = float(data.get("confidence", 0.5))
        if dim in _VALID_DIMENSIONS:
            return {"dimension": dim, "confidence": round(min(max(conf, 0.0), 1.0), 2)}
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # Fallback: buscar la dimensión en texto libre
    match = re.search(r'\b(EC|OR|CA|EA)\b', text.upper())
    if match:
        return {"dimension": match.group(1), "confidence": 0.5}

    return {"dimension": None, "confidence": 0.0}


async def classify_response(
    scenario_title: str,
    scenario_context: str,
    student_response: str,
    ctx: Context,
) -> dict:
    """Usa MCP sampling para clasificar la intención de una respuesta libre del estudiante.

    Cuando el alumno responde con texto abierto (no elige opción A/B/C),
    esta función solicita al LLM cliente que clasifique la respuesta en uno
    de los cuatro pilares Kolb: EC, OR, CA, EA.

    Parámetros
    ----------
    scenario_title:
        Título del escenario actual (ej. "El electrodoméstico nuevo").
    scenario_context:
        Texto del escenario presentado al estudiante.
    student_response:
        Respuesta libre del estudiante.
    ctx:
        Contexto MCP inyectado automáticamente por FastMCP.

    Retorno
    -------
    dict con:
        - ``dimension``  (str | None): pilar Kolb clasificado ("EC", "OR", "CA", "EA")
                                        o None si el LLM no pudo clasificar.
        - ``confidence`` (float):      nivel de confianza entre 0.0 y 1.0.
        - ``raw_response`` (str):      respuesta cruda del LLM (para debugging).
    """
    user_text = _USER_TEMPLATE.format(
        scenario_title=scenario_title,
        scenario_context=scenario_context,
        student_response=student_response,
    )

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=user_text),
            )
        ],
        system_prompt=_SYSTEM_PROMPT,
        max_tokens=64,
        temperature=0.1,
        stop_sequences=["\n\n"],
    )

    raw = ""
    if hasattr(result, "content"):
        content = result.content
        if hasattr(content, "text"):
            raw = content.text
        elif isinstance(content, list) and content:
            raw = getattr(content[0], "text", str(content[0]))

    parsed = _parse_dimension_result(raw)
    return {**parsed, "raw_response": raw}
