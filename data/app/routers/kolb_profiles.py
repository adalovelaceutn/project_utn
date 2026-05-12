from fastapi import APIRouter, HTTPException, status

from app import crud_kolb_profiles, crud_users
from app.schemas import KolbProfileCreate, KolbProfileInDB, KolbProfileUpdate


router = APIRouter(prefix="/api/v1/kolb-profiles", tags=["kolb-profiles"])


@router.post("", response_model=KolbProfileInDB, status_code=status.HTTP_201_CREATED)
async def create_kolb_profile(profile: KolbProfileCreate) -> KolbProfileInDB:
    user = await crud_users.get_user_by_id(profile.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    try:
        return await crud_kolb_profiles.create_profile(profile)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


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
