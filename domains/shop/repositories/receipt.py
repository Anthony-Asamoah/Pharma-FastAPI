from datetime import datetime
from typing import Literal, List

from fastapi import HTTPException, status
from sqlalchemy import desc
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
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            is_refunded: bool = None,
            payment_type: str = None,
            price_from: float = None,
            price_to: float = None,
            time_from: datetime = None,
            time_to: datetime = None,
    ) -> List[Receipt]:

        query = db.query(Receipt)
        try:
            if is_refunded is not None: query = query.filter(Receipt.deleted_at.is_(None) == (not is_refunded))
            if payment_type: query = query.filter(Receipt.payment_type == payment_type)

            if price_from: query = query.filter(Receipt.total_cost >= price_from)
            if price_to: query = query.filter(Receipt.total_cost <= price_to)

            if time_from: query = query.filter(Receipt.created_at >= time_from)
            if time_to: query = query.filter(Receipt.created_at <= time_to)
            if order_by:
                try:
                    order_column = getattr(Receipt, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = query.order_by(desc(Receipt.created_at))

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
