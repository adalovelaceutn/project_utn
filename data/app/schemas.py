from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class KolbDimensions(BaseModel):
    experiencia_concreta: int = Field(..., ge=0, le=100)
    observacion_reflexiva: int = Field(..., ge=0, le=100)
    conceptualizacion_abstracta: int = Field(..., ge=0, le=100)
    experimentacion_activa: int = Field(..., ge=0, le=100)


class KolbProfileBase(BaseModel):
    dni: str = Field(..., min_length=7, max_length=15)
    puntajes: KolbDimensions
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    interview_responses: list[dict] | None = Field(None)

    @field_validator("dni", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()


class KolbProfileCreate(KolbProfileBase):
    pass


class KolbProfileUpdate(BaseModel):
    puntajes: KolbDimensions | None = None
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    interview_responses: list[dict] | None = Field(None)


class KolbProfileInDB(KolbProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    dni: str = Field(..., min_length=7, max_length=15)
    nombre: str = Field(..., min_length=1, max_length=120)
    apellido: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    telefono: str = Field(..., min_length=6, max_length=30)

    @field_validator("username", "dni", "nombre", "apellido", "telefono", mode="before")
    @classmethod
    def trim_user_text(cls, value: str) -> str:
        return value.strip()


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    dni: str | None = Field(None, min_length=7, max_length=15)
    nombre: str | None = Field(None, min_length=1, max_length=120)
    apellido: str | None = Field(None, min_length=1, max_length=120)
    email: EmailStr | None = None
    telefono: str | None = Field(None, min_length=6, max_length=30)
    password: str | None = Field(None, min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
