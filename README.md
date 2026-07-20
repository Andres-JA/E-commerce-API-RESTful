# E-commerce API 

**Escuela Politécnica Nacional — Aplicaciones Web**
Tarea integradora de backend: construcción del API RESTful de e-commerce en tecnología distinta al laboratorio de referencia.

**Tecnología:** Python + FastAPI + SQLAlchemy + PostgreSQL + OAuth2/JWT + OpenAPI (Swagger)

---

## 1. Arquitectura

El proyecto sigue una arquitectura por capas equivalente a la del backend de referencia (Spring Boot):

```
Cliente HTTP
   │
   ▼
app/routers/        → Controladores (endpoints REST, validan entrada vía DTOs)
   │
   ▼
app/services/        → Reglas de negocio (cálculo de total, validación de stock, etc.)
   │
   ▼
app/repositories/    → Acceso a datos (consultas SQLAlchemy)
   │
   ▼
app/models/           → Entidades ORM (User, Product, Receipt, ReceiptItem)
   │
   ▼
PostgreSQL
```

Capas transversales:
- `app/schemas/` → DTOs de entrada/salida (Pydantic).
- `app/exceptions/` → Excepciones de negocio + manejo centralizado de errores.
- `app/core/` → Configuración, conexión a BD, seguridad (hash de contraseñas, JWT).
- `app/dependencies.py` → Autenticación/autorización (usuario actual, admin).

## 2. Entidades

| Entidad | Descripción |
|---|---|
| **User** | Usuarios del sistema. Contraseña cifrada con bcrypt, nunca se devuelve en las respuestas. |
| **Product** | Catálogo de productos, con precio (`Decimal`) y stock. |
| **Receipt** | Recibo/orden de compra de un usuario. `total` calculado en backend. |
| **ReceiptItem** | Detalle de cada recibo: producto, cantidad, precio unitario congelado y subtotal. |

## 3. Reglas de negocio implementadas

- ✅ El cliente **nunca** envía el total ni el precio unitario; el backend los calcula con el precio real almacenado en BD (`app/services/receipt_service.py`).
- ✅ Al crear un recibo se valida stock disponible por cada línea; si no alcanza, se responde `422 INSUFFICIENT_STOCK`.
- ✅ Al confirmar el recibo, el stock se descuenta automáticamente dentro de la misma transacción (con `SELECT ... FOR UPDATE` para evitar condiciones de carrera).
- ✅ Las contraseñas se cifran con **bcrypt** (`passlib`) y jamás se devuelven en las respuestas (DTOs de salida no incluyen `hashed_password`).
- ✅ Montos monetarios manejados con `Numeric(10,2)` / `Decimal` en toda la cadena (evita errores de precisión de `float`).
- ✅ Errores centralizados con formato JSON consistente: `{ "error_code", "message", "path" }`.
- ✅ Autenticación con JWT (OAuth2 Password Flow). Autorización por rol (`customer` / `admin`) y por propiedad del recurso (un usuario solo ve/edita sus propios datos, salvo un admin).

## 4. Endpoints

### Users
| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/api/users/register` | Registro de usuario | Público |
| POST | `/api/users/login` | Login, retorna JWT | Público |
| GET | `/api/users` | Listar usuarios | JWT |
| GET | `/api/users/{id}` | Obtener usuario | JWT (dueño o admin) |
| PUT | `/api/users/{id}` | Actualizar usuario | JWT (dueño o admin) |
| DELETE | `/api/users/{id}` | Eliminar usuario | JWT (dueño o admin) |

### Products
| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/api/products` | Crear producto | JWT admin |
| GET | `/api/products?skip=&limit=&search=` | Listar (paginado + búsqueda) | Público |
| GET | `/api/products/{id}` | Obtener producto | Público |
| PUT | `/api/products/{id}` | Actualizar producto | JWT admin |
| DELETE | `/api/products/{id}` | Eliminar producto | JWT admin |

### Receipts
| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/api/receipts` | Crear recibo (calcula total, descuenta stock) | JWT |
| GET | `/api/receipts` | Listar todos los recibos | JWT admin |
| GET | `/api/receipts/{id}` | Obtener recibo | JWT (dueño o admin) |
| GET | `/api/receipts/user/{userId}` | Recibos de un usuario | JWT (dueño o admin) |
| DELETE | `/api/receipts/{id}` | Eliminar recibo | JWT admin |

> El primer usuario registrado tiene rol `customer` por defecto. Para pruebas de endpoints admin, actualiza manualmente el rol en BD:
> `UPDATE users SET role = 'admin' WHERE username = 'tu_usuario';`

## 5. Requisitos previos

- Python 3.11+
- PostgreSQL 14+ (o Docker)
- pip

## 6. Instalación y ejecución (local)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd ecommerce_api_group2

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL y un SECRET_KEY propio

# 5. Crear la base de datos en PostgreSQL
createdb ecommerce_db
# (o ejecutar manualmente schema.sql en tu cliente de PostgreSQL)

# 6. Crear las tablas
python init_db.py

# 7. Levantar el servidor
uvicorn app.main:app --reload
```

La API quedará disponible en `http://localhost:8000`.

## 7. Ejecución con Docker (recomendado)

```bash
docker-compose up --build
```

Esto levanta PostgreSQL y la API automáticamente. La API estará en `http://localhost:8000`.

## 8. Documentación interactiva (Swagger / OpenAPI)

Con el servidor corriendo:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 9. Pruebas con Postman

Importa la colección incluida en `postman/ecommerce_api_group2.postman_collection.json`.
Incluye variables de colección (`base_url`, `token`, `product_id`, etc.) que se autocompletan
mediante scripts de test al ejecutar Register/Login/Create Product/Create Receipt en orden.

Flujo sugerido:
1. `Users → Register`
2. `Users → Login` (guarda automáticamente el token)
3. (opcional) marcar el usuario como `admin` en BD para probar endpoints protegidos
4. `Products → Create Product`
5. `Receipts → Create Receipt`

## 10. Variables de entorno (`.env`)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión SQLAlchemy | `postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_db` |
| `SECRET_KEY` | Clave secreta para firmar JWT | `una-clave-larga-y-aleatoria` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `60` |
| `BACKEND_CORS_ORIGINS` | Orígenes permitidos CORS | `*` |

## 11. Estructura de carpetas

```
ecommerce_api_group2/
├── app/
│   ├── core/            # config.py, database.py, security.py
│   ├── models/           # Entidades SQLAlchemy
│   ├── schemas/          # DTOs Pydantic
│   ├── repositories/     # Acceso a datos
│   ├── services/         # Reglas de negocio
│   ├── routers/          # Controladores REST
│   ├── exceptions/       # Excepciones + handlers centralizados
│   ├── dependencies.py   # Auth JWT / roles
│   └── main.py           # App FastAPI
├── postman/               # Colección Postman
├── schema.sql              # Script SQL de referencia
├── init_db.py              # Script de creación de tablas
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 12. Notas de diseño y equivalencia con el laboratorio de referencia

| Backend de referencia (Spring Boot) | Este proyecto (FastAPI) |
|---|---|
| Controllers | `app/routers/*.py` |
| Services | `app/services/*.py` |
| Repositories (Spring Data JPA) | `app/repositories/*.py` (SQLAlchemy) |
| Entities (JPA) | `app/models/*.py` (SQLAlchemy ORM) |
| DTOs | `app/schemas/*.py` (Pydantic) |
| `@ControllerAdvice` (manejo global de errores) | `app/exceptions/handlers.py` |
| BCrypt | `passlib[bcrypt]` |
| `BigDecimal` | `Decimal` + `Numeric(10,2)` |
| Spring Security + JWT | OAuth2PasswordBearer + `python-jose` |
| Swagger/OpenAPI (springdoc) | OpenAPI nativo de FastAPI (`/docs`, `/redoc`) |

## 13. Autores

Grupo 2 — Aplicaciones Web — Escuela Politécnica Nacional.
