from __future__ import annotations

from typing import Any

import httpx


class TavilyClient:
    def __init__(self, api_key: str, base_url: str = "https://api.tavily.com") -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    async def search(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        if not self.enabled:
            return []

        payload = {
            "api_key": self._api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            response = await client.post(f"{self._base_url}/search", json=payload)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if not isinstance(results, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                    "content": str(item.get("content", "")).strip(),
                }
            )
        return normalized
