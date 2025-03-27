from sqlalchemy import (
    Column, ForeignKey, UUID, Float
)
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Receipt(BaseModel):
    total_cost = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    items = relationship("Sale", back_populates="receipt")

    @property
    def balance(self):
        return self.total_cost - self.amount_paid
