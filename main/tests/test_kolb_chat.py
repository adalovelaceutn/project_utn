from __future__ import annotations

import pytest

from kolb_main.kolb_chat import build_profile_chat_reply


class _StubMCP:
    async def get_profile_theory(self, style: str) -> dict:
        return {
            "nombre": style,
            "formula": "CA + EA",
            "descripcion": "Aprende aplicando teoria a problemas concretos.",
            "estrategia_agente": "Proponer actividades practicas con retroalimentacion.",
            "descripcion_modelo": "Ciclo entre sentir, observar, pensar y hacer.",
        }


@pytest.mark.asyncio
async def test_build_profile_chat_reply_fallback_without_llm():
    reply = await build_profile_chat_reply(
        message="Que es Kolb?",
        profile={"predominant_style": "Convergente"},
        mcp_client=_StubMCP(),
        llm=None,
        tavily_client=None,
    )
    assert "Convergente" in reply
    assert "Kolb" in reply or "KOLB" in reply


@pytest.mark.asyncio
async def test_build_profile_chat_reply_uses_default_style_when_missing():
    reply = await build_profile_chat_reply(
        message="Dame una recomendacion didactica",
        profile={},
        mcp_client=_StubMCP(),
        llm=None,
        tavily_client=None,
    )
    assert "Convergente" in reply
