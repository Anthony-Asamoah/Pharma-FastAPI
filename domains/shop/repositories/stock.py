from datetime import date
from typing import Literal

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import update, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import log
from crud.base_repository import BaseCRUDRepository
from domains.shop.models.stock import Stock
from domains.shop.schemas.stock import (
    StockCreateInternal, StockUpdateInternal
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class CRUDStock(BaseCRUDRepository[Stock, StockCreateInternal, StockUpdateInternal]):
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
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
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

            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise KeyError(f'Invalid key given to order_by: {order_by}')

                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = query.order_by(desc(self.model.created_at))

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
