from __future__ import annotations

from kolb_main.agent.nodes import _extract_last_agent_text, _extract_profile


def test_extract_last_agent_text_prefers_latest_agent_message():
    task = {
        "messages": [
            {"role": "user", "parts": [{"type": "text", "text": "hola"}]},
            {"role": "agent", "parts": [{"type": "text", "text": "pregunta 1"}]},
        ]
    }
    assert _extract_last_agent_text(task) == "pregunta 1"


def test_extract_profile_reads_data_artifact():
    task = {
        "artifacts": [
            {
                "name": "kolb_profile",
                "parts": [{"type": "data", "data": {"predominant_style": "Convergente"}}],
            }
        ]
    }
    assert _extract_profile(task) == {"predominant_style": "Convergente"}