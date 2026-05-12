from fastapi import APIRouter, HTTPException, status

from app import crud_users
from app.schemas import AuthResponse, UserLogin
from app.security import create_access_token


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin) -> AuthResponse:
    user = await crud_users.authenticate_user(payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    token = create_access_token(user_id=user.id, username=user.username)
    return AuthResponse(access_token=token, user=user)
