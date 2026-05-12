from __future__ import annotations

import httpx


class ProfileAPIClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def get_kolb_profile_by_username_optional(self, username: str) -> dict | None:
        url = f"{self._base_url}/api/v1/kolb-profiles/by-username/{username}/optional"
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return data if isinstance(data, dict) else None
