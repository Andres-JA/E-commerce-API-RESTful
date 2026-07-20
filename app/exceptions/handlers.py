"""
Manejo centralizado de errores. Todas las excepciones de la API
responden con un formato JSON consistente:

{
    "error_code": "NOT_FOUND",
    "message": "Producto no encontrado",
    "path": "/api/products/99"
}
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions.custom_exceptions import (
    AppException,
    NotFoundException,
    ConflictException,
    InsufficientStockException,
    InvalidCredentialsException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
)

_STATUS_MAP = {
    "NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "CONFLICT": status.HTTP_409_CONFLICT,
    "INSUFFICIENT_STOCK": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "INVALID_CREDENTIALS": status.HTTP_401_UNAUTHORIZED,
    "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
    "FORBIDDEN": status.HTTP_403_FORBIDDEN,
    "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "APP_ERROR": status.HTTP_400_BAD_REQUEST,
}


def _error_body(error_code: str, message: str, path: str) -> dict:
    return {"error_code": error_code, "message": message, "path": path}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        http_status = _STATUS_MAP.get(exc.error_code, status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=http_status,
            content=_error_body(exc.error_code, exc.message, str(request.url.path)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Errores de validación de Pydantic/FastAPI (body/query/path mal formados)
        details = [
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("VALIDATION_ERROR", "; ".join(details), str(request.url.path)),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body(
                "CONFLICT", "Violación de restricción de integridad en la base de datos", str(request.url.path)
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("INTERNAL_SERVER_ERROR", "Ocurrió un error inesperado en el servidor", str(request.url.path)),
        )
