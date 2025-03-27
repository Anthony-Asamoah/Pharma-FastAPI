from datetime import date, datetime, time
from typing import Optional, Any, Dict

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Sale
class SaleBase(BaseModel):
    quantity: Optional[int] = None
    payment_type: Optional[str] = "CASH"
    cost: Optional[float] = None
    item_id: Optional[UUID4] = None
    receipt_id: Optional[UUID4] = None
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class SaleCreate(SaleBase):
    quantity: int
    cost: float
    item_id: UUID4
    receipt_id: UUID4
    created_by_id: UUID4


# Properties to receive via API on update
class SaleUpdate(SaleBase):
    pass


# Additional properties to return via API
class SaleSchema(SaleBase, BaseSchema):
    pass
