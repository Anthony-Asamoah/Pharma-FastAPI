from crud.base_repository import BaseCRUDRepository
from domains.shop.models.stock import Stock
from domains.shop.schemas.stock import (
    StockCreate, StockUpdate
)


class CRUDStock(BaseCRUDRepository[Stock, StockCreate, StockUpdate]):
    pass


stock_actions = CRUDStock(Stock)
