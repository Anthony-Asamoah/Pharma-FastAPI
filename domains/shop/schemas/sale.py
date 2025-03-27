from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Sale
class SaleBase(BaseModel):
    quantity: Optional[int] = None
    payment_type: Optional[str] = "CASH"
    item_id: Optional[UUID4] = None
    receipt_id: Optional[UUID4] = None
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class SaleCreate(SaleBase):
    quantity: int
    item_id: UUID4
    receipt_id: UUID4
    created_by_id: UUID4


class SaleCreateInternal(SaleCreate):
    cost: float


# Properties to receive via API on update
class SaleUpdate(SaleBase):
    pass


# Additional properties to return via API
class SaleSchema(SaleBase, BaseSchema):
    cost: Optional[float] = None
