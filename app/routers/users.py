from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.exceptions.custom_exceptions import ForbiddenException
from app.models.user import User
from app.schemas.token import TokenDTO
from app.schemas.user import (
    UserRegisterDTO,
    UserLoginDTO,
    UserUpdateDTO,
    UserResponseDTO,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


def _ensure_self_or_admin(target_user_id: int, current_user: User) -> None:
    if current_user.id != target_user_id and current_user.role != "admin":
        raise ForbiddenException("No tiene permisos para operar sobre este usuario")


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def register(dto: UserRegisterDTO, db: Session = Depends(get_db)):
    """Registra un nuevo usuario. La contraseña se cifra antes de persistirse."""
    return UserService(db).register(dto)


@router.post("/login", response_model=TokenDTO)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna un JWT (OAuth2 Password Flow).
    Recibe form-data (username, password) en lugar de JSON: es el formato
    que exige el estándar OAuth2 y el que usa el botón "Authorize" de Swagger.
    """
    dto = UserLoginDTO(username=form_data.username, password=form_data.password)
    token = UserService(db).login(dto)
    return TokenDTO(access_token=token)


@router.get("", response_model=List[UserResponseDTO])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista usuarios (requiere autenticación)."""
    return UserService(db).list_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un usuario por id. El propio usuario o un admin pueden verlo."""
    _ensure_self_or_admin(user_id, current_user)
    return UserService(db).get_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(
    user_id: int,
    dto: UserUpdateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza datos del usuario. Solo el propio usuario o un admin."""
    _ensure_self_or_admin(user_id, current_user)
    return UserService(db).update(user_id, dto)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un usuario. Solo el propio usuario o un admin."""
    _ensure_self_or_admin(user_id, current_user)
    UserService(db).delete(user_id)
