from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.exceptions.custom_exceptions import (
    ConflictException,
    NotFoundException,
    InvalidCredentialsException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegisterDTO, UserUpdateDTO, UserLoginDTO


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, dto: UserRegisterDTO) -> User:
        if self.repo.get_by_username(dto.username):
            raise ConflictException("El nombre de usuario ya está registrado")
        if self.repo.get_by_email(dto.email):
            raise ConflictException("El correo electrónico ya está registrado")

        user = User(
            username=dto.username,
            email=dto.email,
            full_name=dto.full_name,
            hashed_password=hash_password(dto.password),
        )
        return self.repo.create(user)

    def login(self, dto: UserLoginDTO) -> str:
        user = self.repo.get_by_username(dto.username)
        if not user or not verify_password(dto.password, user.hashed_password):
            raise InvalidCredentialsException("Usuario o contraseña incorrectos")
        if not user.is_active:
            raise InvalidCredentialsException("El usuario está inactivo")
        return create_access_token(subject=str(user.id))

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"Usuario con id {user_id} no encontrado")
        return user

    def list_all(self, skip: int = 0, limit: int = 100):
        return self.repo.list_all(skip=skip, limit=limit)

    def update(self, user_id: int, dto: UserUpdateDTO) -> User:
        user = self.get_by_id(user_id)

        if dto.email and dto.email != user.email:
            if self.repo.get_by_email(dto.email):
                raise ConflictException("El correo electrónico ya está registrado")
            user.email = dto.email

        if dto.full_name is not None:
            user.full_name = dto.full_name

        if dto.password:
            user.hashed_password = hash_password(dto.password)

        return self.repo.update(user)

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        self.repo.delete(user)
