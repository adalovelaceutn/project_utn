from __future__ import annotations

from typing import Any

import httpx


class ProfilerA2AClient:
    def __init__(self, base_url: str, timeout_seconds: int = 45) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def send_task(self, task_id: str, text: str, metadata: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": text}],
                },
                "metadata": metadata,
            },
        }

        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.post(f"{self._base_url}/", json=payload)
            response.raise_for_status()
            data = response.json()

        if data.get("error"):
            raise RuntimeError(data["error"].get("message", "A2A request failed"))
        return data["result"]