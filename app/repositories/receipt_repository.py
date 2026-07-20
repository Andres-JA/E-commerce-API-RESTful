from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.receipt import Receipt


class ReceiptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, receipt_id: int) -> Optional[Receipt]:
        return (
            self.db.query(Receipt)
            .options(joinedload(Receipt.items))
            .filter(Receipt.id == receipt_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Receipt)
            .options(joinedload(Receipt.items))
            .order_by(Receipt.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Receipt)
            .options(joinedload(Receipt.items))
            .filter(Receipt.user_id == user_id)
            .order_by(Receipt.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, receipt: Receipt) -> Receipt:
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        return receipt

    def delete(self, receipt: Receipt) -> None:
        self.db.delete(receipt)
        self.db.commit()
