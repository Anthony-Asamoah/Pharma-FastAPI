from crud.base_repository import BaseCRUDRepository
from domains.shop.models.expenses import Expenses
from domains.shop.schemas.expenses import (
    ExpensesCreate, ExpensesUpdate
)


class CRUDExpenses(BaseCRUDRepository[Expenses, ExpensesCreate, ExpensesUpdate]):
    pass


expenses_actions = CRUDExpenses(Expenses)
