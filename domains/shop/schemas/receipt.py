from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema
from domains.common.schema.related import RelatedUserSchema, RelatedSaleSchema


# Receipt
class ReceiptBase(BaseModel):
    amount_paid: Optional[float] = None
    payment_type: Optional[str] = "CASH"


# Properties to receive via API on creation
class ReceiptCreate(ReceiptBase):
    amount_paid: float


class ReceiptCreateInternal(ReceiptCreate):
    total_cost: float


# Properties to receive via API on update
class ReceiptUpdate(ReceiptBase):
    pass


class ReceiptUpdateInternal(ReceiptBase):
    total_cost: Optional[float] = None


# Additional properties to return via API
class VanillaReceiptSchema(ReceiptBase, BaseSchema):
    total_cost: Optional[float] = None
    balance: Optional[float] = None
    created_by_id: Optional[UUID4] = None


class ReceiptSchema(VanillaReceiptSchema):
    created_by: Optional[RelatedUserSchema] = None
    items: Optional[List[RelatedSaleSchema]] = None


# Full Schema to create a receipt
class RelatedSaleCreate(BaseModel):
    quantity: int
    item_id: UUID4


class ReceiptCreateWithSales(ReceiptCreate):
    items: List[RelatedSaleCreate]
