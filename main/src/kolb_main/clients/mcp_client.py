from __future__ import annotations

import json

import httpx


class MainMCPClient:
    """Cliente MCP (streamable-http) para obtener teoría Kolb desde main."""

    def __init__(self, mcp_server_url: str) -> None:
        self._base_url = mcp_server_url.rstrip("/")
        self._session_id: str | None = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    @staticmethod
    def _parse_payload(resp: httpx.Response) -> dict:
        """Parsea respuesta MCP en JSON o en frames SSE."""
        try:
            return resp.json()
        except ValueError:
            text = resp.text or ""
            data_lines = [
                line[len("data:") :].strip()
                for line in text.splitlines()
                if line.startswith("data:")
            ]
            if data_lines:
                return json.loads(data_lines[-1])
            raise

    async def initialize(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "kolb-main", "version": "0.1.0"},
            },
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                self._base_url,
                json=payload,
                headers={"Accept": "application/json, text/event-stream"},
            )
            resp.raise_for_status()
            self._session_id = resp.headers.get("mcp-session-id")

    async def get_profile_theory(self, style: str) -> dict:
        if self._session_id is None:
            await self.initialize()

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "kolb_profile_theory",
                "arguments": {"style": style},
            },
        }
        headers = {"Accept": "application/json, text/event-stream"}
        if self._session_id:
            headers["mcp-session-id"] = self._session_id

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                self._base_url,
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = self._parse_payload(resp)

        result = data.get("result", {})
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and content:
                raw = content[0].get("text", "{}")
                return json.loads(raw)

        return result if isinstance(result, dict) else {}
