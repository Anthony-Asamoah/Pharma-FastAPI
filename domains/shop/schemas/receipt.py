from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema
from domains.shop.schemas.sale import SaleSchema


# Receipt
class ReceiptBase(BaseModel):
    amount_paid: Optional[float] = None
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class ReceiptCreate(ReceiptBase):
    amount_paid: float
    created_by_id: UUID4


class ReceiptCreateInternal(ReceiptBase):
    total_cost: float


# Properties to receive via API on update
class ReceiptUpdate(ReceiptBase):
    pass


class ReceiptUpdateInternal(ReceiptBase):
    total_cost: float


# Additional properties to return via API
class ReceiptSchema(ReceiptBase, BaseSchema):
    total_cost: Optional[float] = None
    items: Optional[List[SaleSchema]]


# Full Schema to create a receipt
class RelatedSaleCreate(BaseModel):
    quantity: int
    item_id: UUID4


class ReceiptCreateWithSales(ReceiptCreate):
    items: List[RelatedSaleCreate]
