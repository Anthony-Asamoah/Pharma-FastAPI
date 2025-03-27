from crud.base_repository import BaseCRUDRepository
from domains.shop.models.stock import Stock
from domains.shop.schemas.stock import (
    StockCreateInternal, StockUpdateInternal
)


class CRUDStock(BaseCRUDRepository[Stock, StockCreateInternal, StockUpdateInternal]):
    pass


stock_actions = CRUDStock(Stock)
