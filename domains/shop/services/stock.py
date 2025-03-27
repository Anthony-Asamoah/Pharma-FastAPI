from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.stock import stock_actions as stock_repo
from domains.shop.schemas.stock import StockSchema, StockUpdate, StockCreate


class StockService:

    def __init__(self):
        self.repo = stock_repo

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

    async def create_stock(self, db: Session, *, data: StockCreate) -> StockSchema:
        stock = await self.repo.create(db=db, data=data)
        return stock

    async def update_stock(self, db: Session, *, id: UUID4, data: StockUpdate) -> StockSchema:
        stock = await self.repo.get_by_id(db=db, id=id)
        stock = await self.repo.update(db=db, db_obj=stock, data=data)
        return stock

    async def get_stock(self, db: Session, *, id: UUID4) -> StockSchema:
        stock = await self.repo.get_by_id(db=db, id=id)
        return stock

    async def delete_stock(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

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
