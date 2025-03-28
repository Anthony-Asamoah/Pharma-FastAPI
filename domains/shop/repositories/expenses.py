from datetime import datetime
from typing import Optional, Literal, List

from fastapi import HTTPException, status
from sqlalchemy import desc
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
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
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
            if order_by:
                try:
                    order_column = getattr(Expenses, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = query.order_by(desc(Expenses.created_at))

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

expenses_actions = CRUDExpenses(Expenses)
