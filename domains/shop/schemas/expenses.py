from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Expenses
class ExpensesBase(BaseModel):
    expense: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    created_by_id: Optional[UUID4] = None


# Properties to receive via API on creation
class ExpensesCreate(ExpensesBase):
    expense: str
    price: float
    created_by_id: UUID4


# Properties to receive via API on update
class ExpensesUpdate(ExpensesBase):
    pass


# Additional properties to return via API
class ExpensesSchema(ExpensesBase, BaseSchema):
    pass
