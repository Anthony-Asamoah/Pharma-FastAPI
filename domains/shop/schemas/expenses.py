from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Expenses
class ExpensesBase(BaseModel):
    expense: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    paid_at: Optional[datetime] = Field(default=None)


# Properties to receive via API on creation
class ExpensesCreate(ExpensesBase):
    expense: str
    price: float


# Properties to receive via API on update
class ExpensesUpdate(ExpensesBase):
    pass


# Additional properties to return via API
class ExpensesSchema(ExpensesBase, BaseSchema):
    created_by_id: Optional[UUID4] = None
