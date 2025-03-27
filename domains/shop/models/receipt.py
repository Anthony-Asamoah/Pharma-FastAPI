from sqlalchemy import (
    Column, ForeignKey, UUID, Float, String
)
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Receipt(BaseModel):
    total_cost = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    payment_type = Column(String(250), default="CASH")

    created_by = relationship("User")
    items = relationship("Sale", back_populates="receipt")

    @property
    def balance(self):
        return self.amount_paid - self.total_cost
