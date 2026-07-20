"""
Script de inicialización de base de datos.
Crea todas las tablas definidas en los modelos SQLAlchemy usando la
DATABASE_URL configurada en .env

Uso:
    python init_db.py
"""
from app.core.database import Base, engine
from app import models  # noqa: F401  (necesario para registrar los modelos en Base.metadata)


def main():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    main()
