from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions.custom_exceptions import NotFoundException, InsufficientStockException
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.repositories.product_repository import ProductRepository
from app.repositories.receipt_repository import ReceiptRepository
from app.repositories.user_repository import UserRepository
from app.schemas.receipt import ReceiptCreateDTO


class ReceiptService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReceiptRepository(db)
        self.product_repo = ProductRepository(db)
        self.user_repo = UserRepository(db)

    def create(self, user_id: int, dto: ReceiptCreateDTO) -> Receipt:
        """
        Regla de negocio central:
        1. El cliente NUNCA envía precios ni el total.
        2. Se valida stock disponible para cada línea.
        3. El total se calcula 100% en el backend con los precios reales de BD.
        4. El stock se descuenta automáticamente al confirmar el recibo.
        Todo ocurre dentro de una única transacción: si algo falla, se revierte todo.
        """
        if not self.user_repo.get_by_id(user_id):
            raise NotFoundException(f"Usuario con id {user_id} no encontrado")

        try:
            total = Decimal("0.00")
            receipt_items = []
            products_to_update = []

            for item_dto in dto.items:
                # Bloquea la fila para evitar condiciones de carrera en el stock
                product = self.product_repo.get_by_id_for_update(item_dto.product_id)
                if not product:
                    raise NotFoundException(
                        f"Producto con id {item_dto.product_id} no encontrado"
                    )
                if product.stock < item_dto.quantity:
                    raise InsufficientStockException(
                        f"Stock insuficiente para '{product.name}'. "
                        f"Disponible: {product.stock}, solicitado: {item_dto.quantity}"
                    )

                unit_price = product.price  # precio real tomado de la BD, no del cliente
                subtotal = (unit_price * item_dto.quantity).quantize(Decimal("0.01"))
                total += subtotal

                receipt_items.append(
                    ReceiptItem(
                        product_id=product.id,
                        quantity=item_dto.quantity,
                        unit_price=unit_price,
                        subtotal=subtotal,
                    )
                )

                # Descuento automático de stock
                product.stock -= item_dto.quantity
                products_to_update.append(product)

            receipt = Receipt(user_id=user_id, total=total, status="CONFIRMED", items=receipt_items)
            self.db.add(receipt)
            self.db.commit()
            self.db.refresh(receipt)
            return receipt
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, receipt_id: int) -> Receipt:
        receipt = self.repo.get_by_id(receipt_id)
        if not receipt:
            raise NotFoundException(f"Recibo con id {receipt_id} no encontrado")
        return receipt

    def list_all(self, skip: int = 0, limit: int = 100):
        return self.repo.list_all(skip=skip, limit=limit)

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        if not self.user_repo.get_by_id(user_id):
            raise NotFoundException(f"Usuario con id {user_id} no encontrado")
        return self.repo.list_by_user(user_id, skip=skip, limit=limit)

    def delete(self, receipt_id: int) -> None:
        receipt = self.get_by_id(receipt_id)
        self.repo.delete(receipt)
