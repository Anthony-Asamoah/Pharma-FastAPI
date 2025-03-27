from crud.base_repository import BaseCRUDRepository
from domains.shop.models.sale import Sale
from domains.shop.schemas.sale import (
    SaleCreate, SaleUpdate
)


class CRUDSale(BaseCRUDRepository[Sale, SaleCreate, SaleUpdate]):
    pass


sale_actions = CRUDSale(Sale)
