from datetime import date, datetime, time
from typing import Optional, Any, Dict

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Receipt
class ReceiptBase(BaseModel):
    total_cost: Optional[float] = None
    amount_paid: Optional[float] = None
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class ReceiptCreate(ReceiptBase):
    total_cost: float
    amount_paid: float
    created_by_id: UUID4


# Properties to receive via API on update
class ReceiptUpdate(ReceiptBase):
    pass


# Additional properties to return via API
class ReceiptSchema(ReceiptBase, BaseSchema):
    pass
