from datetime import datetime
from typing import List, Optional

import pendulum
from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.expenses import expenses_actions as expenses_repo
from domains.shop.schemas.dashboard import ExpensesSummarySchema
from domains.shop.schemas.expenses import ExpensesSchema, ExpensesUpdate, ExpensesCreate


class ExpensesService:

    def __init__(self):
        self.repo = expenses_repo

    async def list_expenses(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            search: str = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            price_range_min: float = None,
            price_range_max: float = None,
            is_deleted: bool = None,
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_all(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            is_deleted=is_deleted,
            order_by=order_by,
            time_range_min=time_range_min,
            time_range_max=time_range_max,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
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
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return expense

    async def search_expenses(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[ExpensesSchema]:
        expense = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return expense

    async def assemble_dash(self, db: Session) -> ExpensesSummarySchema:
        return ExpensesSummarySchema(
            monthly_net=await self.repo.get_expenses_amount_for_date_range(
                db=db,
                time_range_min=pendulum.today()._first_of_month(),
                time_range_max=pendulum.today()._last_of_month(),
            ),
            daily_net=await self.repo.get_expenses_amount_for_date_range(
                db=db,
                time_range_min=pendulum.today(),
                time_range_max=pendulum.tomorrow(),
            )
        )


expenses_service = ExpensesService()
