from crud.base_repository import BaseCRUDRepository
from domains.shop.models.receipt import Receipt
from domains.shop.schemas.receipt import (
    ReceiptCreate, ReceiptUpdate
)


class CRUDReceipt(BaseCRUDRepository[Receipt, ReceiptCreate, ReceiptUpdate]):
    pass


receipt_actions = CRUDReceipt(Receipt)
