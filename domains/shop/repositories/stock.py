from pydantic import UUID4
from sqlalchemy import update
from sqlalchemy.orm import Session

from crud.base_repository import BaseCRUDRepository
from domains.shop.models.stock import Stock
from domains.shop.schemas.stock import (
    StockCreateInternal, StockUpdateInternal
)


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


stock_actions = CRUDStock(Stock)
