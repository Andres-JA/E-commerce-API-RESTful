"""
Configuración centralizada de la aplicación.
Lee variables de entorno (o archivo .env) usando pydantic-settings.
"""
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce API - Grupo 2 (FastAPI)"
    API_V1_PREFIX: str = "/api"

    # Base de datos
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_db"

    # JWT
    SECRET_KEY: str = "cambia-esta-clave-super-secreta-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v != "*":
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
