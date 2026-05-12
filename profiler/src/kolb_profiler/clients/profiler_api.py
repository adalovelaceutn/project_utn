from __future__ import annotations

import httpx


class ProfilerAPIClient:
    """Async HTTP client for the FastAPI Kolb profile endpoints."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_profile(self, profile: dict) -> str:
        """POST /api/v1/kolb-profiles and return the created profile id."""
        print(f"Creating profile with DNI on {self._base_url}/api/v1/kolb-profiles:", profile.get("dni"))
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/kolb-profiles",
                json=profile,
            )
            resp.raise_for_status()
            return resp.json()["id"]

    async def get_profile_by_dni(self, dni: str) -> dict | None:
        """GET /api/v1/kolb-profiles/by-dni/{dni}/optional."""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/kolb-profiles/by-dni/{dni}/optional"
            )
            resp.raise_for_status()
            return resp.json()

    async def update_profile(self, profile_id: str, profile: dict) -> str:
        """PATCH /api/v1/kolb-profiles/{profile_id} and return the profile id."""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.patch(
                f"{self._base_url}/api/v1/kolb-profiles/{profile_id}",
                json=profile,
            )
            resp.raise_for_status()
            return resp.json()["id"]

    async def upsert_profile(self, profile: dict) -> str:
        print("Upsert profile with DNI:", profile.get("dni"))
        """Create or update a Kolb profile by unique dni."""
        existing = await self.get_profile_by_dni(profile["dni"])
        if existing and existing.get("id"):
            update_payload = {
                "puntajes": profile["puntajes"],
                "confidence_score": profile.get("confidence_score"),
                "interview_responses": profile.get("interview_responses"),
            }
            print("Updating profile with ID:", existing["id"], "Payload:", update_payload)
            return await self.update_profile(existing["id"], update_payload)
        print("Creating new profile with DNI:", profile.get("dni"))
        return await self.create_profile(profile)
