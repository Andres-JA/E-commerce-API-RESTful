from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.product import ProductCreateDTO, ProductUpdateDTO, ProductResponseDTO
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.post("", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED)
def create_product(
    dto: ProductCreateDTO,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Crea un producto. Requiere rol admin."""
    return ProductService(db).create(dto)


@router.get("", response_model=List[ProductResponseDTO])
def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista productos con paginación y búsqueda opcional (valor agregado). Acceso público."""
    return ProductService(db).list_all(skip=skip, limit=limit, search=search)


@router.get("/{product_id}", response_model=ProductResponseDTO)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto por id. Acceso público."""
    return ProductService(db).get_by_id(product_id)


@router.put("/{product_id}", response_model=ProductResponseDTO)
def update_product(
    product_id: int,
    dto: ProductUpdateDTO,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Actualiza un producto. Requiere rol admin."""
    return ProductService(db).update(product_id, dto)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Elimina un producto. Requiere rol admin."""
    ProductService(db).delete(product_id)
