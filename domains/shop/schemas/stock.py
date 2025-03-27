from datetime import date
from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Stock
class StockBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None
    issues: Optional[int] = 0
    total_issues_cost: Optional[float] = 0
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class StockCreate(StockBase):
    name: str
    purchase_price: float
    selling_price: float
    quantity: int
    expiry_date: date
    created_by_id: UUID4


# Properties to receive via API on update
class StockUpdate(StockBase):
    pass


# Additional properties to return via API
class StockSchema(StockBase, BaseSchema):
    pass
