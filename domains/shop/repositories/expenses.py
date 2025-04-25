from datetime import datetime
from typing import Optional, Literal, List

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import log
from crud.base_repository import BaseCRUDRepository, ModelType
from domains.shop.models.expenses import Expenses
from domains.shop.schemas.expenses import (
    ExpensesCreate, ExpensesUpdate
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class CRUDExpenses(BaseCRUDRepository[Expenses, ExpensesCreate, ExpensesUpdate]):
    async def get_all(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            search: str = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            price_range_min: float = None,
            price_range_max: float = None,
            is_deleted: bool = None
    ) -> List[ModelType]:

        query = db.query(Expenses)
        try:
            if is_deleted is not None: query = query.filter(Expenses.deleted_at.isnot(None) == is_deleted)
            if search: query = query.filter(Expenses.expense.ilike(f"%{search.strip()}%"))

            if price_range_min: query = query.filter(Expenses.price >= price_range_min)
            if price_range_max: query = query.filter(Expenses.price <= price_range_max)

            if time_range_min: query = query.filter(Expenses.paid_at >= time_range_min)
            if time_range_max: query = query.filter(Expenses.created_at <= time_range_max)

            query = await self._get_ordering(query=query, order_by=order_by)
            results = query.offset(skip).limit(limit).all()

            return results
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {Expenses.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {Expenses.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_expenses_amount_for_date_range(
            self, db: Session, *,
            time_range_min: datetime,
            time_range_max: datetime,
    ) -> float:
        query = (
            db.query(func.sum(Expenses.price))
            .filter(Expenses.paid_at >= time_range_min)
            .filter(Expenses.paid_at <= time_range_max)
            .filter(Expenses.deleted_at.is_(None))
        )
        result = query.scalar() or 0.0
        return round(result, 2)


expenses_actions = CRUDExpenses(Expenses)
