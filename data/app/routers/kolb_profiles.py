from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import ValidationError

from app import crud_kolb_profiles, crud_users
from app.schemas import KolbProfileCreate, KolbProfileInDB, KolbProfileUpdate


router = APIRouter(prefix="/api/v1/kolb-profiles", tags=["kolb-profiles"])
legacy_router = APIRouter(prefix="/api/v1/profiler", tags=["kolb-profiles-legacy"])


def _to_int_score(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0

    # Accept 0..1 normalized values from legacy clients.
    if 0.0 <= number <= 1.0:
        number = number * 100
    return max(0, min(100, int(round(number))))


def _normalize_scores(payload: dict[str, Any]) -> dict[str, int]:
    source = payload.get("puntajes") or payload.get("scores") or payload.get("kolb_dimensions") or {}
    if not isinstance(source, dict):
        source = {}

    return {
        "experiencia_concreta": _to_int_score(
            source.get("experiencia_concreta")
            or source.get("CE")
            or source.get("EC")
            or 0
        ),
        "observacion_reflexiva": _to_int_score(
            source.get("observacion_reflexiva")
            or source.get("RO")
            or source.get("OR")
            or 0
        ),
        "conceptualizacion_abstracta": _to_int_score(
            source.get("conceptualizacion_abstracta")
            or source.get("AC")
            or source.get("CA")
            or 0
        ),
        "experimentacion_activa": _to_int_score(
            source.get("experimentacion_activa")
            or source.get("AE")
            or source.get("EA")
            or 0
        ),
    }


def _normalize_confidence(payload: dict[str, Any]) -> float | None:
    raw = payload.get("confidence_score")
    if raw is None:
        raw = payload.get("confidence")
    if raw is None:
        return None

    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None

    # Legacy clients may send confidence as percentage (0..100).
    if number > 1.0:
        number = number / 100.0
    return max(0.0, min(1.0, number))


async def _normalize_legacy_profile(payload: dict[str, Any]) -> KolbProfileCreate:
    user_id = payload.get("user_id") or payload.get("student_id") or payload.get("id")
    username = payload.get("username") or payload.get("user_name")

    if not user_id and username:
        user = await crud_users.get_user_by_username(str(username))
        if user is not None:
            user_id = user.id

    normalized = {
        "user_id": str(user_id or "").strip(),
        "alumno_id": str(payload.get("alumno_id") or payload.get("dni") or user_id or username or "").strip(),
        "nombre": str(payload.get("nombre") or payload.get("full_name") or username or "Sin nombre").strip(),
        "email": str(payload.get("email") or "sin-informar@example.com").strip(),
        "carrera": str(payload.get("carrera") or payload.get("career") or "Sin informar").strip(),
        "puntajes": _normalize_scores(payload),
        "predominant_style": payload.get("predominant_style") or payload.get("style"),
        "confidence_score": _normalize_confidence(payload),
        "interview_responses": payload.get("interview_responses") or payload.get("interview") or [],
    }

    return KolbProfileCreate.model_validate(normalized)


@router.post("", response_model=KolbProfileInDB, status_code=status.HTTP_201_CREATED)
async def create_kolb_profile(profile: KolbProfileCreate) -> KolbProfileInDB:
    user = await crud_users.get_user_by_id(profile.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    try:
        return await crud_kolb_profiles.create_profile(profile)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@legacy_router.post("/", response_model=KolbProfileInDB, status_code=status.HTTP_201_CREATED)
async def create_kolb_profile_legacy(payload: dict[str, Any] = Body(...)) -> KolbProfileInDB:
    # Backward-compatible path used by older profiler clients with varying payload schemas.
    try:
        profile = await _normalize_legacy_profile(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc
    return await create_kolb_profile(profile)


@router.get("", response_model=list[KolbProfileInDB])
async def list_kolb_profiles() -> list[KolbProfileInDB]:
    return await crud_kolb_profiles.list_profiles()


@router.get("/{profile_id}", response_model=KolbProfileInDB)
async def get_kolb_profile(profile_id: str) -> KolbProfileInDB:
    profile = await crud_kolb_profiles.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.get("/by-student/{alumno_id}", response_model=KolbProfileInDB)
async def get_kolb_profile_by_alumno_id(alumno_id: str) -> KolbProfileInDB:
    profile = await crud_kolb_profiles.get_profile_by_alumno_id(alumno_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.get("/by-user/{user_id}", response_model=KolbProfileInDB)
async def get_kolb_profile_by_user_id(user_id: str) -> KolbProfileInDB:
    profile = await crud_kolb_profiles.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.get("/by-user/{user_id}/optional", response_model=KolbProfileInDB | None)
async def get_kolb_profile_by_user_id_optional(user_id: str) -> KolbProfileInDB | None:
    return await crud_kolb_profiles.get_profile_by_user_id(user_id)


@router.get("/by-username/{username}", response_model=KolbProfileInDB)
async def get_kolb_profile_by_username(username: str) -> KolbProfileInDB:
    user = await crud_users.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    profile = await crud_kolb_profiles.get_profile_by_user_id(user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.get("/by-username/{username}/optional", response_model=KolbProfileInDB | None)
async def get_kolb_profile_by_username_optional(username: str) -> KolbProfileInDB | None:
    user = await crud_users.get_user_by_username(username)
    if user is None:
        return None
    return await crud_kolb_profiles.get_profile_by_user_id(user.id)


@router.put("/{profile_id}", response_model=KolbProfileInDB)
async def update_kolb_profile(profile_id: str, data: KolbProfileUpdate) -> KolbProfileInDB:
    profile = await crud_kolb_profiles.update_profile(profile_id, data)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.patch("/{profile_id}", response_model=KolbProfileInDB)
async def patch_kolb_profile(profile_id: str, data: KolbProfileUpdate) -> KolbProfileInDB:
    profile = await crud_kolb_profiles.update_profile(profile_id, data)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kolb_profile(profile_id: str) -> None:
    deleted = await crud_kolb_profiles.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
