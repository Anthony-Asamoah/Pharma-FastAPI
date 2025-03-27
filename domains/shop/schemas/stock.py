from datetime import date
from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema
from domains.common.schema.related import RelatedUserSchema


# Stock
class StockBase(BaseModel):
    ref: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None


# Properties to receive via API on creation
class StockCreate(StockBase):
    ref: Optional[str] = None
    name: str
    purchase_price: float
    selling_price: float
    quantity: int
    expiry_date: date


class StockCreateInternal(StockCreate):
    issues: Optional[int] = 0
    total_issues_cost: Optional[float] = 0


# Properties to receive via API on update
class StockUpdate(StockBase):
    pass


class StockUpdateInternal(StockBase):
    issues: Optional[int] = 0
    total_issues_cost: Optional[float] = 0


# Additional properties to return via API
class VanillaStockSchema(StockBase, BaseSchema):
    created_by_id: Optional[UUID4] = None
    issues: Optional[int] = 0
    total_issues_cost: Optional[float] = 0
    stock_value: Optional[float] = None
    expected_stock_balance: Optional[float] = None
    expected_profit: Optional[float] = None
    is_expired: bool
    is_available: bool
    days_to_expiry: int


class StockSchema(VanillaStockSchema):
    created_by: RelatedUserSchema
