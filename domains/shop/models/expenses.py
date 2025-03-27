from sqlalchemy import (
    Column, String, Float, ForeignKey, UUID, Text
)

from db.table import BaseModel


class Expenses(BaseModel):
    expense = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_by_id = Column(UUID, ForeignKey("users.id"), nullable=False)
