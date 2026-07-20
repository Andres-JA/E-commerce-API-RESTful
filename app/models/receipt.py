from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # El total SIEMPRE se calcula en el backend a partir de los precios reales en BD
    total = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="CONFIRMED")  # CONFIRMED | CANCELLED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
