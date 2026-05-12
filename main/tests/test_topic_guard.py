from __future__ import annotations

import pytest

from kolb_main.topic_guard import is_topic_allowed


@pytest.mark.asyncio
async def test_topic_allowed_by_kolb_keyword_without_llm():
    allowed = await is_topic_allowed(
        "Como aplicar Kolb en una clase de laboratorio?",
        profile={"predominant_style": "Convergente"},
        llm=None,
    )
    assert allowed is True


@pytest.mark.asyncio
async def test_topic_blocked_without_llm_if_not_kolb_related():
    allowed = await is_topic_allowed(
        "Quien gano el partido anoche?",
        profile={"predominant_style": "Convergente"},
        llm=None,
    )
    assert allowed is False
