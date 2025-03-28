from datetime import datetime
from typing import Optional

from pydantic import UUID4
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.base_repository import BaseCRUDRepository
from domains.shop.models.sale import Sale
from domains.shop.schemas.sale import (
    SaleUpdate, SaleCreateInternal
)


class CRUDSale(BaseCRUDRepository[Sale, SaleCreateInternal, SaleUpdate]):

    async def get_sales_amount_for_date_range(
            self, db: Session, *,
            time_range_min: datetime,
            time_range_max: datetime,
            payment_types: Optional[list[str]] = None
    ) -> float:
        query = (
            db.query(func.sum(Sale.cost))
            .filter(Sale.created_at >= time_range_min)
            .filter(Sale.created_at <= time_range_max)
            .filter(Sale.deleted_at.is_(None))
        )
        if payment_types: query = query.filter(Sale.payment_type.in_(payment_types))
        result = query.scalar() or 0.0
        return round(result, 2)

    async def get_sales_count_for_stock(self, db: Session, stock_id: UUID4) -> int:
        query = (
            db.query(Sale)
            .filter(Sale.item_id == stock_id)
            .filter(Sale.deleted_at.is_(None))
            .count()
        )
        return query

    async def get_total_sales_amount_for_stock(self, db: Session, stock_id: UUID4) -> float:
        total_sales_amount = (
                db.query(func.sum(Sale.cost))
                .filter(Sale.item_id == stock_id)
                .filter(Sale.deleted_at.is_(None))
                .scalar() or 0.0
        )
        return total_sales_amount


sale_actions = CRUDSale(Sale)
