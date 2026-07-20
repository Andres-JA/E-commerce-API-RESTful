from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegisterDTO(BaseModel):
    """DTO de entrada para registro de usuario. Nunca se acepta un hash aquí."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=150)
    password: str = Field(min_length=6, max_length=128)


class UserLoginDTO(BaseModel):
    username: str
    password: str


class UserUpdateDTO(BaseModel):
    """Todos los campos opcionales: actualización parcial."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=150)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)


class UserResponseDTO(BaseModel):
    """DTO de salida. NUNCA incluye la contraseña ni su hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
