import pendulum
from sqlalchemy import (
    Column, Integer, Date, String, DateTime, Float, Text, UUID, ForeignKey
)
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Stock(BaseModel):
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=False)
    issues = Column(Integer, default=0)
    total_issues_cost = Column(Float, default=0)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    sale = relationship("Sale", back_populates="item")

    @property
    def stock_value(self):
        return round(self.purchase_price * self.quantity)

    @property
    def expected_stock_balance(self):
        return round(self.quantity * self.selling_price, 2)

    @property
    def expected_profit(self):
        return round(self.expected_stock_balance - self.stock_value, 2)
