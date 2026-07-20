from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import NotFoundException
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreateDTO, ProductUpdateDTO


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def create(self, dto: ProductCreateDTO) -> Product:
        product = Product(
            name=dto.name,
            description=dto.description,
            price=dto.price,
            stock=dto.stock,
        )
        return self.repo.create(product)

    def get_by_id(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundException(f"Producto con id {product_id} no encontrado")
        return product

    def list_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        return self.repo.list_all(skip=skip, limit=limit, search=search)

    def update(self, product_id: int, dto: ProductUpdateDTO) -> Product:
        product = self.get_by_id(product_id)

        if dto.name is not None:
            product.name = dto.name
        if dto.description is not None:
            product.description = dto.description
        if dto.price is not None:
            product.price = dto.price
        if dto.stock is not None:
            product.stock = dto.stock

        return self.repo.update(product)

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.repo.delete(product)
