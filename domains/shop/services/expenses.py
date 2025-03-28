from datetime import datetime
from typing import List, Optional, Literal

import pendulum
from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.expenses import expenses_actions as expenses_repo
from domains.shop.schemas.expenses import ExpensesSchema, ExpensesUpdate, ExpensesCreate


class ExpensesService:

    def __init__(self):
        self.repo = expenses_repo

    async def list_expenses(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            search: str = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            price_range_min: float = None,
            price_range_max: float = None,
            is_deleted: bool = None,
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_all(
            db=db, skip=skip, limit=limit, search=search, is_deleted=is_deleted,
            order_by=order_by, order_direction=order_direction,
            time_range_min=time_range_min, time_range_max=time_range_max,
            price_range_min=price_range_min, price_range_max=price_range_max,
        )
        return expense

    async def create_expenses(self, db: Session, *, data: ExpensesCreate, created_by_id: UUID4) -> ExpensesSchema:
        if not data.paid_at: data.paid_at = pendulum.now()
        expenses = await self.repo.create(db=db, data=data, created_by_id=created_by_id)
        return expenses

    async def update_expenses(self, db: Session, *, id: UUID4, data: ExpensesUpdate) -> ExpensesSchema:
        expenses = await self.repo.get_by_id(db=db, id=id)
        expenses = await self.repo.update(db=db, db_obj=expenses, data=data)
        return expenses

    async def get_expenses(self, db: Session, *, id: UUID4) -> ExpensesSchema:
        expenses = await self.repo.get_by_id(db=db, id=id)
        return expenses

    async def delete_expenses(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_expenses_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return expense

    async def search_expenses(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return expense


expenses_service = ExpensesService()
