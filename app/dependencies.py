from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.exceptions.custom_exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Extrae y valida el JWT del header Authorization, retorna el usuario autenticado."""
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token inválido o expirado")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token inválido: no contiene información del usuario")

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException("Usuario no encontrado o inactivo")

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Restringe el acceso a usuarios con rol 'admin'."""
    if current_user.role != "admin":
        raise ForbiddenException("Se requieren privilegios de administrador")
    return current_user
