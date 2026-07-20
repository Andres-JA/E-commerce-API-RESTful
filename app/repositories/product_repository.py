from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def list_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = self.db.query(Product)
        if search:
            like = f"%{search}%"
            query = query.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))
        return query.offset(skip).limit(limit).all()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    def get_by_id_for_update(self, product_id: int) -> Optional[Product]:
        """
        Bloquea la fila del producto (SELECT ... FOR UPDATE) para evitar
        condiciones de carrera al descontar stock concurrentemente.
        En SQLite (usado solo para pruebas locales) with_for_update se ignora.
        """
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .with_for_update()
            .first()
        )
