from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import log
from crud.base_repository import BaseCRUDRepository
from domains.shop.models.receipt import Receipt
from domains.shop.schemas.receipt import (
    ReceiptCreateInternal, ReceiptUpdateInternal
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class CRUDReceipt(BaseCRUDRepository[Receipt, ReceiptCreateInternal, ReceiptUpdateInternal]):
    async def get_all(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            is_refunded: bool = None,
            payment_type: str = None,
            price_from: float = None,
            price_to: float = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
    ) -> List[Receipt]:

        query = db.query(Receipt)
        try:
            if is_refunded is not None: query = query.filter(Receipt.deleted_at.isnot(None) == is_refunded)
            if payment_type: query = query.filter(Receipt.payment_type == payment_type)

            if price_from: query = query.filter(Receipt.total_cost >= price_from)
            if price_to: query = query.filter(Receipt.total_cost <= price_to)

            if time_range_min: query = query.filter(Receipt.created_at >= time_range_min)
            if time_range_max: query = query.filter(Receipt.created_at <= time_range_max)

            query = await self._get_ordering(query=query, order_by=order_by)
            results = query.offset(skip).limit(limit).all()

            return results
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {Receipt.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {Receipt.__name__}")
            raise await http_500_exc_internal_server_error()


receipt_actions = CRUDReceipt(Receipt)
