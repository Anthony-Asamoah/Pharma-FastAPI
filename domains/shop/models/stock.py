from uuid import uuid4

import pendulum
from sqlalchemy import (
    Column, Integer, Date, String, Float, Text, UUID, ForeignKey
)
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Stock(BaseModel):
    ref = Column(String, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=False)
    issues = Column(Integer, default=0)
    total_issues_cost = Column(Float, default=0)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    created_by = relationship("User")
    sales = relationship("Sale", back_populates="item")

    @property
    def stock_value(self) -> float:
        return round(self.purchase_price * self.quantity)

    @property
    def expected_stock_balance(self) -> float:
        return round(self.quantity * self.selling_price, 2)

    @property
    def expected_profit(self) -> float:
        return round(self.expected_stock_balance - self.stock_value, 2)

    @property
    def is_expired(self) -> bool:
        return self.expiry_date <= pendulum.now().date()

    @property
    def days_to_expiry(self) -> int:
        if self.is_expired: return 0
        today = pendulum.today().date()
        if today > self.expiry_date: return 0
        return (self.expiry_date - today).days

    @property
    def is_available(self) -> bool:
        if self.is_expired: return False
        if self.quantity <= 0: return False
        return True
