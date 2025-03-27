from crud.base_repository import BaseCRUDRepository
from domains.shop.models.receipt import Receipt
from domains.shop.schemas.receipt import (
    ReceiptCreateInternal, ReceiptUpdateInternal
)


class CRUDReceipt(BaseCRUDRepository[Receipt, ReceiptCreateInternal, ReceiptUpdateInternal]):
    pass


receipt_actions = CRUDReceipt(Receipt)
