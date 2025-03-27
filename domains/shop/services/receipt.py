import asyncio
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from config.settings import settings
from domains.shop.repositories.receipt import receipt_actions as receipt_repo
from domains.shop.schemas.receipt import ReceiptSchema, ReceiptUpdate, ReceiptCreateWithSales, ReceiptCreateInternal, \
    VanillaReceiptSchema
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
            order_direction: Literal['asc', 'desc'] = 'asc',
            is_refunded: bool = None,
            payment_type: str = None,
            price_from: float = None,
            price_to: float = None,
            time_from: datetime = None,
            time_to: datetime = None,
    ) -> List[VanillaReceiptSchema]:
        receipts = await self.repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction,
            time_from=time_from, time_to=time_to,
            price_from=price_from, price_to=price_to,
            is_refunded=is_refunded, payment_type=payment_type
        )
        return receipts

    async def create_receipt(self, db: Session, *, data: ReceiptCreateWithSales, created_by_id: UUID4) -> ReceiptSchema:
        # get stock info
        items = await stock_service.repo.get_many_by_ids(db=db, ids=[item.item_id for item in data.items])

        # get dictionary of stock/item id for each sale and merge duplicates' quantities
        map_data_items_to_item_id = {}
        for item in data.items:
            if duplicate := map_data_items_to_item_id.get(str(item.item_id)):
                duplicate.quantity += item.quantity
                map_data_items_to_item_id[str(item.item_id)] = duplicate
            else:
                map_data_items_to_item_id[str(item.item_id)] = item

        # perform validations
        for item in items:
            if not item.is_available: raise ValueError(
                f"{item.name.title()} is currently not available."
            )
            update_obj = map_data_items_to_item_id.get(str(item.id), None)
            if update_obj and update_obj.quantity > item.quantity: raise ValueError(
                f"{item.name.title()} is currently not available. Short of {update_obj.quantity - item.quantity}"
            )

        total_cost = sum([item.selling_price * map_data_items_to_item_id[str(item.id)].quantity for item in items])
        if total_cost > data.amount_paid: raise ValueError(
            "Paid amount should be more than the total cost."
        )

        # create receipt obj
        receipt = await self.repo.create(
            db=db,
            created_by_id=created_by_id,
            data=ReceiptCreateInternal(
                **data.model_dump(exclude_none=True),
                total_cost=total_cost,
            ))

        # create associated sales
        await asyncio.gather(*[
            sale_service.create_sale(db=db, data=SaleCreate(
                quantity=item.quantity,
                item_id=item.item_id,
                receipt_id=receipt.id,
                payment_type=receipt.payment_type,
                created_by_id=created_by_id,
            )) for item in data.items
        ])
        return receipt

    async def update_receipt(self, db: Session, *, id: UUID4, data: ReceiptUpdate) -> ReceiptSchema:
        receipt = await self.repo.get_by_id(db=db, id=id)
        receipt = await self.repo.update(db=db, db_obj=receipt, data=data)
        return receipt

    async def get_receipt(self, db: Session, *, id: UUID4) -> ReceiptSchema:
        receipt = await self.repo.get_by_id(db=db, id=id)
        return receipt

    async def delete_receipt(self, db: Session, *, id: UUID4) -> None:
        receipt = await self.repo.get_by_id(db=db, id=id)
        sales = await sale_service.get_sale_by_keywords(db=db, receipt_id=receipt.id)
        for sale in sales:
            await sale_service.delete_sale(db=db, id=sale.id)
        await self.repo.delete(db=db, db_obj=receipt, soft=True)

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
