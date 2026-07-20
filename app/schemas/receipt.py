from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class ReceiptItemCreateDTO(BaseModel):
    """
    El cliente SOLO envía product_id y quantity.
    El precio unitario y el subtotal se calculan siempre en el backend
    a partir del precio real almacenado en la base de datos.
    """

    product_id: int
    quantity: int = Field(gt=0, description="Cantidad debe ser mayor a 0")


class ReceiptCreateDTO(BaseModel):
    """
    DTO de entrada para crear un recibo. NO incluye total: el total
    lo calcula el backend sumando los subtotales reales.
    """

    items: List[ReceiptItemCreateDTO] = Field(min_length=1)


class ReceiptItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class ReceiptResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total: Decimal
    status: str
    created_at: datetime
    items: List[ReceiptItemResponseDTO] = []
