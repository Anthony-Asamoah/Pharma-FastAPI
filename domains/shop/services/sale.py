from datetime import datetime
from typing import List, Optional, Literal

import pendulum
from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.sale import sale_actions as sale_repo
from domains.shop.schemas.dashboard import SaleSummarySchema
from domains.shop.schemas.sale import SaleSchema, SaleUpdate, SaleCreate, SaleCreateInternal
from domains.shop.services.stock import stock_service


class SaleService:

    def __init__(self):
        self.repo = sale_repo

    async def get_sales_count_for_stock(self, db: Session, stock_id: UUID4 = None) -> int:
        sales_count = await self.repo.get_sales_count_for_stock(db=db, stock_id=stock_id)
        return sales_count

    async def get_total_sales_amount_for_stock(self, db: Session, stock_id: UUID4 = None) -> float:
        sales_amount = await self.repo.get_total_sales_amount_for_stock(db=db, stock_id=stock_id)
        return sales_amount

    async def list_sales(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            is_refunded: bool = False
    ) -> List[SaleSchema]:
        sales = await self.repo.get_all(
            db=db,
            skip=skip,
            limit=limit,
            order_by=order_by,
            time_range_min=time_range_min,
            time_range_max=time_range_max,
            is_deleted=is_refunded,
        )
        return sales

    async def create_sale(self, db: Session, *, data: SaleCreate) -> SaleSchema:
        item = await stock_service.get_stock(db=db, id=data.item_id)
        sale = await self.repo.create(db=db, data=SaleCreateInternal(
            **data.model_dump(),
            cost=item.selling_price * data.quantity
        ))
        await stock_service.sell_an_item(db=db, id=sale.item_id, quantity=data.quantity)
        return sale

    async def update_sale(self, db: Session, *, id: UUID4, data: SaleUpdate) -> SaleSchema:
        sale = await self.repo.get_by_id(db=db, id=id)
        sale = await self.repo.update(db=db, db_obj=sale, data=data)
        return sale

    async def get_sale(self, db: Session, *, id: UUID4) -> SaleSchema:
        sale = await self.repo.get_by_id(db=db, id=id)
        return sale

    async def delete_sale(self, db: Session, *, id: UUID4) -> None:
        sale = await self.repo.get_by_id(db=db, id=id)
        await stock_service.return_an_item(db=db, id=sale.item_id, quantity=sale.quantity)
        await self.repo.delete(db=db, id=id, soft=True)

    async def get_sale_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[SaleSchema]:
        sales = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return sales

    async def search_sales(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[SaleSchema]:
        sales = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return sales

    async def assemble_dash(self, db: Session) -> SaleSummarySchema:
        daily_time_range_min = pendulum.today()
        daily_time_range_max = pendulum.tomorrow()

        monthly_time_range_min = pendulum.today()._first_of_month()
        monthly_time_range_max = pendulum.today()._last_of_month()
        return SaleSummarySchema(
            monthly_net=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=monthly_time_range_min,
                time_range_max=monthly_time_range_max,
            ),
            monthly_momo=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=monthly_time_range_min,
                time_range_max=monthly_time_range_max,
                payment_types=["MTN_MOMO", "VODAFONE CASH", "AT MONEY"]
            ),
            monthly_cash=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=monthly_time_range_min,
                time_range_max=monthly_time_range_max,
                payment_types=["CASH"]
            ),
            daily_net=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=daily_time_range_min,
                time_range_max=daily_time_range_max,
            ),
            daily_momo=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=daily_time_range_min,
                time_range_max=daily_time_range_max,
                payment_types=["MTN_MOMO", "VODAFONE CASH", "AT MONEY"]
            ),
            daily_cash=await self.repo.get_sales_amount_for_date_range(
                db=db,
                time_range_min=daily_time_range_min,
                time_range_max=daily_time_range_max,
                payment_types=["CASH"]
            ),
        )


sale_service = SaleService()
