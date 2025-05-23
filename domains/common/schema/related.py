from typing import Optional

from pydantic import BaseModel, UUID4


class RelatedUserSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class RelatedStockSchema(BaseModel):
    id: UUID4
    name: Optional[str] = None
    description: Optional[str] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    is_available: bool


class RelatedSaleSchema(BaseModel):
    quantity: Optional[int] = None
    cost: Optional[float] = None
    item: RelatedStockSchema
