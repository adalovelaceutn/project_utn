from __future__ import annotations

import httpx


class ProfilerAPIClient:
    """Async HTTP client for the FastAPI /api/v1/profiler endpoint."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_profile(self, profile: dict) -> str:
        """POST /api/v1/profiler and return the created profile id."""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/profiler/",
                json=profile,
            )
            resp.raise_for_status()
            return resp.json()["id"]

    async def get_profile_by_student(self, student_id: str) -> dict | None:
        """GET /api/v1/profiler/student/{student_id}."""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/profiler/student/{student_id}"
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
