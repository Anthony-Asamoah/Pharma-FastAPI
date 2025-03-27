from sqlalchemy import (
    Column, String, UUID, ForeignKey, Integer, Float
)
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Sale(BaseModel):
    quantity = Column(Integer, nullable=False)
    payment_type = Column(String(250), default="CASH")
    cost = Column(Float, nullable=False)
    item_id = Column(UUID, ForeignKey("stocks.id"), nullable=False)
    receipt_id = Column(UUID, ForeignKey("receipts.id"), nullable=False)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    item = relationship("Stock", back_populates="sales")
    receipt = relationship("Receipt", back_populates="items")
