from datetime import date
from typing import List, Optional, Literal
from uuid import uuid4

import pendulum
from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.stock import stock_actions as stock_repo
from domains.shop.schemas.dashboard import TotalStockValueAndDailySaleSchema
from domains.shop.schemas.stock import StockSchema, StockUpdate, StockCreate, StockUpdateInternal, VanillaStockSchema


class StockService:

    def __init__(self):
        self.repo = stock_repo

    async def sell_an_item(self, db: Session, *, id: UUID4, quantity: int) -> None:
        await self.repo.sell_an_item(db=db, id=id, quantity=quantity)
        await self.update_stock(db=db, id=id, data=StockUpdate())

    async def return_an_item(self, db: Session, *, id: UUID4, quantity: int) -> None:
        await self.repo.return_an_item(db=db, id=id, quantity=quantity)
        await self.update_stock(db=db, id=id, data=StockUpdate())

    async def get_by_reference(self, db: Session, *, ref: str, silent=False) -> Optional[StockSchema]:
        return await self.repo.get_by_field(db=db, field="ref", value=ref, silent=silent)

    async def list_stocks(
            self, db: Session, *,
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
    ) -> List[VanillaStockSchema]:
        stocks = await self.repo.get_all(
            db=db, skip=skip, limit=limit, search=search,
            order_by=order_by, order_direction=order_direction,
            quantity_min=quantity_min, quantity_max=quantity_max,
            expiry_date_min=expiry_date_min, expiry_date_max=expiry_date_max,
            selling_price_min=selling_price_min, selling_price_max=selling_price_max,
        )
        return stocks

    async def create_stock(self, db: Session, *, data: StockCreate, created_by_id: UUID4) -> StockSchema:
        # perform validations
        if data.purchase_price >= data.selling_price: raise ValueError(
            "Selling price should be greater than purchase price"
        )
        if not data.ref: data.ref = str(uuid4())
        if not isinstance(data.ref, str): data.ref = str(uuid4())
        stock = await self.repo.create(db=db, data=data, created_by_id=created_by_id)
        return stock

    async def update_stock(self, db: Session, *, id: UUID4, data: StockUpdate) -> StockSchema:
        stock = await self.repo.get_by_id(db=db, id=id)
        stock = await self.repo.update(db=db, db_obj=stock, data=data)
        # set values
        from domains.shop.services.sale import sale_service
        payload = StockUpdateInternal(**data.model_dump())
        payload.issues = await sale_service.get_sales_count_for_stock(db=db, stock_id=stock.id)
        payload.total_issues_cost = await sale_service.get_total_sales_amount_for_stock(db=db, stock_id=stock.id)
        stock = await self.repo.update(db=db, db_obj=stock, data=payload)
        return stock

    async def get_stock(self, db: Session, *, id: UUID4) -> StockSchema:
        stock = await self.repo.get_by_id(db=db, id=id)
        return stock

    async def delete_stock(self, db: Session, *, id: UUID4, soft=True) -> None:
        await self.repo.delete(db=db, id=id, soft=soft)

    async def get_stock_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[StockSchema]:
        stocks = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return stocks

    async def search_stocks(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[StockSchema]:
        stocks = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return stocks

    async def assemble_dash(
            self, db: Session
    ) -> TotalStockValueAndDailySaleSchema:
        from domains.shop.services.sale import sale_service

        # default period is 1 day
        time_range_min = pendulum.today()
        time_range_max = pendulum.tomorrow()

        return TotalStockValueAndDailySaleSchema(
            total_purchase_price=await self.repo.get_total_purchase_price(db=db),
            total_sell_price=await sale_service.repo.get_sales_amount_for_date_range(
                db=db, time_range_min=time_range_min, time_range_max=time_range_max
            ),
        )


stock_service = StockService()
