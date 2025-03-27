from pydantic import UUID4
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.base_repository import BaseCRUDRepository
from domains.shop.models.sale import Sale
from domains.shop.schemas.sale import (
    SaleCreate, SaleUpdate
)


class CRUDSale(BaseCRUDRepository[Sale, SaleCreate, SaleUpdate]):
    async def get_sales_count_for_stock(self, db: Session, stock_id: UUID4) -> int:
        query = (
            db.query(Sale)
            .filter(Sale.item_id == stock_id)
            .count()
        )
        return query

    async def get_total_sales_amount_for_stock(self, db: Session, stock_id: UUID4) -> float:
        total_sales_amount = (
                db.query(func.sum(Sale.cost))
                .filter(Sale.item_id == stock_id)
                .scalar() or 0.0
        )
        return total_sales_amount


sale_actions = CRUDSale(Sale)
