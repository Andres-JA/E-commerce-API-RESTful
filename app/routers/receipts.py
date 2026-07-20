from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.exceptions.custom_exceptions import ForbiddenException
from app.models.user import User
from app.schemas.receipt import ReceiptCreateDTO, ReceiptResponseDTO
from app.services.receipt_service import ReceiptService

router = APIRouter(prefix="/api/receipts", tags=["Receipts"])


@router.post("", response_model=ReceiptResponseDTO, status_code=status.HTTP_201_CREATED)
def create_receipt(
    dto: ReceiptCreateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un recibo para el usuario autenticado.
    El total se calcula en el backend y el stock se descuenta automáticamente.
    """
    return ReceiptService(db).create(current_user.id, dto)


@router.get("", response_model=List[ReceiptResponseDTO])
def list_receipts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Lista todos los recibos del sistema. Requiere rol admin."""
    return ReceiptService(db).list_all(skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[ReceiptResponseDTO])
def list_receipts_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista los recibos de un usuario. Accesible por el propio usuario o un admin."""
    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenException("No tiene permisos para ver los recibos de este usuario")
    return ReceiptService(db).list_by_user(user_id, skip=skip, limit=limit)


@router.get("/{receipt_id}", response_model=ReceiptResponseDTO)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un recibo por id. Accesible por el dueño del recibo o un admin."""
    service = ReceiptService(db)
    receipt = service.get_by_id(receipt_id)
    if current_user.id != receipt.user_id and current_user.role != "admin":
        raise ForbiddenException("No tiene permisos para ver este recibo")
    return receipt


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Elimina un recibo. Requiere rol admin."""
    ReceiptService(db).delete(receipt_id)
