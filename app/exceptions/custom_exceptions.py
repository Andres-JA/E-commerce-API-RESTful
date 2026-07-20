"""
Excepciones de dominio/negocio. Se lanzan desde la capa de servicios
y son traducidas a respuestas HTTP consistentes por los handlers globales.
"""


class AppException(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, message: str, error_code: str = "APP_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, error_code="NOT_FOUND")


class ConflictException(AppException):
    """Ej: username/email ya registrados."""

    def __init__(self, message: str = "Conflicto con el estado actual del recurso"):
        super().__init__(message, error_code="CONFLICT")


class InsufficientStockException(AppException):
    def __init__(self, message: str = "Stock insuficiente para completar la operación"):
        super().__init__(message, error_code="INSUFFICIENT_STOCK")


class InvalidCredentialsException(AppException):
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message, error_code="INVALID_CREDENTIALS")


class UnauthorizedException(AppException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, error_code="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, message: str = "Acceso prohibido"):
        super().__init__(message, error_code="FORBIDDEN")


class ValidationException(AppException):
    def __init__(self, message: str = "Datos de entrada inválidos"):
        super().__init__(message, error_code="VALIDATION_ERROR")
