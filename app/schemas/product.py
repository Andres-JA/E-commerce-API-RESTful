from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProductCreateDTO(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(gt=0, description="Precio unitario, debe ser mayor a 0")
    stock: int = Field(ge=0, description="Stock inicial, no puede ser negativo")

    @field_validator("price")
    @classmethod
    def round_price(cls, v: Decimal) -> Decimal:
        return round(v, 2)


class ProductUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)

    @field_validator("price")
    @classmethod
    def round_price(cls, v):
        return round(v, 2) if v is not None else v


class ProductResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    created_at: datetime
