from fastapi import APIRouter, HTTPException, status

from app import crud_kolb_profiles
from app import crud_users
from app.schemas import UserCreate, UserPublic, UserUpdate


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> UserPublic:
    try:
        return await crud_users.create_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("", response_model=list[UserPublic])
async def list_users() -> list[UserPublic]:
    return await crud_users.list_users()


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: str) -> UserPublic:
    user = await crud_users.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(user_id: str, payload: UserUpdate) -> UserPublic:
    try:
        user = await crud_users.update_user(user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
async def patch_user(user_id: str, payload: UserUpdate) -> UserPublic:
    try:
        user = await crud_users.update_user(user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str) -> None:
    await crud_kolb_profiles.delete_profile_by_user_id(user_id)
    deleted = await crud_users.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
