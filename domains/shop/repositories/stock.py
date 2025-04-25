from datetime import date, datetime
from typing import Optional, List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import update, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import log
from crud.base_repository import BaseCRUDRepository
from domains.shop.models import Sale
from domains.shop.models.stock import Stock
from domains.shop.schemas.stock import (
    StockCreateInternal, StockUpdateInternal
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class CRUDStock(BaseCRUDRepository[Stock, StockCreateInternal, StockUpdateInternal]):

    async def list_most_issued_stock(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 5,
            time_range_min: Optional[datetime],
            time_range_max: Optional[datetime],
    ) -> List[Stock]:
        query = (
            db.query(Stock, func.count(Sale.id).label('sales_count'))
            .join(Sale, Stock.id == Sale.item_id)
            .filter(Stock.deleted_at.is_(None))
            .group_by(Stock.id)
        )
        if time_range_min: query = query.filter(Sale.created_at >= time_range_min)
        if time_range_max: query = query.filter(Sale.created_at <= time_range_max)

        query = query.order_by(desc('sales_count')).offset(skip).limit(limit).all()
        results = [item[0] for item in query]
        return results

    async def list_most_profitable_stock(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 5,
            time_range_min: Optional[datetime],
            time_range_max: Optional[datetime],
    ) -> List[Stock]:
        query = (
            db.query(Stock, func.sum(Sale.cost).label('total_profit'))
            .join(Sale, Stock.id == Sale.item_id)
            .filter(Stock.deleted_at.is_(None))
            .group_by(Stock.id)
        )
        if time_range_min: query = query.filter(Sale.created_at >= time_range_min)
        if time_range_max: query = query.filter(Sale.created_at <= time_range_max)

        query = query.order_by(desc('total_profit')).offset(skip).limit(limit).all()
        results = [item[0] for item in query]
        return results

    async def list_most_refunded_stock(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 5,
            time_range_min: Optional[datetime],
            time_range_max: Optional[datetime],
    ) -> List[Stock]:
        query = (
            db.query(Stock, func.sum(Sale.quantity).label('total_refunded'))
            .join(Sale, Stock.id == Sale.item_id)
            .filter(Stock.deleted_at.is_(None))
            .filter(Sale.deleted_at.isnot(None))  # Only include refunded sales
            .group_by(Stock.id)
        )
        if time_range_min: query = query.filter(Sale.deleted_at >= time_range_min)
        if time_range_max: query = query.filter(Sale.deleted_at <= time_range_max)

        query = query.order_by(desc('total_refunded')).offset(skip).limit(limit).all()

        results = [item[0] for item in query]
        return results

    async def list_soon_expiring_stock(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 5,
            time_range_min: Optional[datetime],
            time_range_max: Optional[datetime],
    ) -> List[Stock]:
        query = db.query(Stock).order_by(desc(Stock.expiry_date))
        if time_range_min: query = query.filter(Stock.expiry_date >= time_range_min)
        if time_range_max: query = query.filter(Stock.expiry_date <= time_range_max)
        results = query.offset(skip).limit(limit).all()
        return results

    async def get_total_stock_value(
            self, db: Session,
            time_range_min: datetime = None,
            time_range_max: datetime = None
    ) -> float:
        query = (db.query(func.sum(Stock.purchase_price * Stock.quantity))
                 .filter(Stock.deleted_at.is_(None)))
        if time_range_min: query = query.filter(Stock.created_at >= time_range_min)  # Fixed comparison direction
        if time_range_max: query = query.filter(Stock.created_at <= time_range_max)  # Fixed comparison direction
        result = query.scalar() or 0.00
        return round(result, 2)

    async def get_expected_return_amount(self, db: Session) -> float:
        query = (
            db.query(func.sum(Stock.selling_price * Stock.quantity))
            .filter(Stock.deleted_at.is_(None))
        )
        result = query.scalar() or 0.00
        return round(result, 2)

    async def return_an_item(self, db: Session, id: UUID4, quantity: int) -> None:
        db.execute(
            update(Stock)
            .where(Stock.id == id)
            .values(quantity=Stock.quantity + quantity)
        )

    async def sell_an_item(self, db: Session, id: UUID4, quantity: int) -> None:
        db.execute(
            update(Stock)
            .where(Stock.id == id)
            .values(quantity=Stock.quantity - quantity)
        )

    async def get_all(
            self, db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            search: str = None,
            quantity_min: int = None,
            quantity_max: int = None,
            expiry_date_min: date = None,
            expiry_date_max: date = None,
            selling_price_min: float = None,
            selling_price_max: float = None,
    ):
        query = db.query(self.model)
        try:
            if search: query = query.filter(Stock.name.ilike(f"%{search.strip()}%"))

            if selling_price_min is not None: query = query.filter(Stock.selling_price >= selling_price_min)
            if selling_price_max is not None: query = query.filter(Stock.selling_price <= selling_price_max)

            if quantity_min is not None: query = query.filter(Stock.quantity >= quantity_min)
            if quantity_max is not None: query = query.filter(Stock.quantity <= quantity_max)

            if expiry_date_min is not None: query = query.filter(Stock.expiry_date >= expiry_date_min)
            if expiry_date_max is not None: query = query.filter(Stock.expiry_date <= expiry_date_max)

            query = await self._get_ordering(query=query, order_by=order_by)
            results = query.offset(skip).limit(limit).all()

            return results
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise await http_500_exc_internal_server_error()


stock_actions = CRUDStock(Stock)
