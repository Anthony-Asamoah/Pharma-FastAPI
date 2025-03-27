from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.stock import stock_actions as stock_repo
from domains.shop.schemas.stock import StockSchema, StockUpdate, StockCreate, StockUpdateInternal


class StockService:

    def __init__(self):
        self.repo = stock_repo

    async def sell_an_item(self, db: Session, id: UUID4, quantity: int) -> None:
        await self.repo.sell_an_item(db=db, id=id, quantity=quantity)
        await self.update_stock(db=db, id=id, data=StockUpdate())

    async def return_an_item(self, db: Session, id: UUID4, quantity: int) -> None:
        await self.repo.return_an_item(db=db, id=id, quantity=quantity)
        await self.update_stock(db=db, id=id, data=StockUpdate())

    async def list_stocks(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[StockSchema]:
        stocks = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return stocks

    async def create_stock(self, db: Session, *, data: StockCreate, created_by_id: UUID4) -> StockSchema:
        # perform validations
        if data.purchase_price >= data.selling_price: raise ValueError(
            "Selling price should be greater than purchase price"
        )
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

        stock = await self.repo.update(db=db, db_obj=stock, data=data)
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


stock_service = StockService()
