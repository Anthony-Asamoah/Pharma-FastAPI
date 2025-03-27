import asyncio
from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.shop.repositories.receipt import receipt_actions as receipt_repo
from domains.shop.schemas.receipt import ReceiptSchema, ReceiptUpdate, ReceiptCreateWithSales
from domains.shop.schemas.sale import SaleCreate
from domains.shop.services.sale import sale_service
from domains.shop.services.stock import stock_service


class ReceiptService:

    def __init__(self):
        self.repo = receipt_repo

    async def list_receipts(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[ReceiptSchema]:
        receipts = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return receipts

    async def create_receipt(self, db: Session, *, data: ReceiptCreateWithSales, created_by: UUID4) -> ReceiptSchema:
        receipt = await self.repo.create(db=db, data=data)

        # create associated sales
        items = await stock_service.repo.get_many_by_ids(db=db, ids=[item.item_id for item in data.items])
        items_map = {item.id: item for item in items}

        await asyncio.gather(*[
            sale_service.create_sale(db=db, data=SaleCreate(
                cost=round(item.quantity * items_map[item.item_id].selling_price, 2),
                quantity=item.quantity,
                item_id=item.item_id,
                receipt_id=receipt.id,
                created_by_id=created_by,
            )) for item in data.items
        ])
        receipt = await self.get_receipt(db=db, id=receipt.id)
        return receipt

    async def update_receipt(self, db: Session, *, id: UUID4, data: ReceiptUpdate) -> ReceiptSchema:
        receipt = await self.repo.get_by_id(db=db, id=id)
        receipt = await self.repo.update(db=db, db_obj=receipt, data=data)
        return receipt

    async def get_receipt(self, db: Session, *, id: UUID4) -> ReceiptSchema:
        receipt = await self.repo.get_by_id(db=db, id=id)
        return receipt

    async def delete_receipt(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_receipt_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[ReceiptSchema]:
        receipts = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return receipts

    async def search_receipts(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[ReceiptSchema]:
        receipts = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return receipts


receipt_service = ReceiptService()
