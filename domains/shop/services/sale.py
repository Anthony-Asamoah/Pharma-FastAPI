from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.sale import sale_actions as sale_repo
from domains.shop.schemas.sale import SaleSchema, SaleUpdate, SaleCreate
from domains.shop.services.stock import stock_service


class SaleService:

    def __init__(self):
        self.repo = sale_repo

    async def get_sales_count_for_stock(self, db: Session, stock_id: UUID4 = None) -> int:
        sales_count = await self.repo.get_sales_count_for_stock(db=db, stock_id=stock_id)
        return sales_count

    async def get_total_sales_amount_for_stock(self, db: Session, stock_id: UUID4 = None) -> int:
        sales_amount = await self.repo.get_total_sales_amount_for_stock(db=db, stock_id=stock_id)
        return sales_amount

    async def list_sales(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[SaleSchema]:
        sales = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return sales

    async def create_sale(self, db: Session, *, data: SaleCreate) -> SaleSchema:
        if not data.cost:
            item = await stock_service.get_stock(db=db, id=data.item_id)
            data.cost = item.selling_price * data.quantity
        sale = await self.repo.create(db=db, data=data)
        return sale

    async def update_sale(self, db: Session, *, id: UUID4, data: SaleUpdate) -> SaleSchema:
        sale = await self.repo.get_by_id(db=db, id=id)
        sale = await self.repo.update(db=db, db_obj=sale, data=data)
        return sale

    async def get_sale(self, db: Session, *, id: UUID4) -> SaleSchema:
        sale = await self.repo.get_by_id(db=db, id=id)
        return sale

    async def delete_sale(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_sale_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[SaleSchema]:
        sales = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return sales

    async def search_sales(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[SaleSchema]:
        sales = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return sales


sale_service = SaleService()
