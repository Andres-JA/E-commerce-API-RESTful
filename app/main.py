"""
E-commerce API - Grupo 2
Tecnología: Python + FastAPI + SQLAlchemy + PostgreSQL + OAuth2/JWT + OpenAPI

Arquitectura por capas:
    routers (controladores) -> services (reglas de negocio) -> repositories (acceso a datos) -> models (ORM)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.exceptions.handlers import register_exception_handlers
from app.routers import users, products, receipts

# Crea las tablas si no existen (además del script/migración incluidos en el repo)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API RESTful de E-commerce (Users, Products, Receipts, ReceiptItems) "
        "construida con FastAPI, SQLAlchemy, PostgreSQL y JWT, como equivalente "
        "funcional del backend de referencia en Spring Boot."
    ),
    version="1.0.0",
    contact={"name": "Grupo 2 - EPN - Aplicaciones Web"},
)

# CORS
origins = settings.BACKEND_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins == "*" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejo centralizado de errores
register_exception_handlers(app)

# Routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(receipts.router)


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint simple para verificar que la API está en ejecución."""
    return {"status": "ok", "service": settings.PROJECT_NAME}
