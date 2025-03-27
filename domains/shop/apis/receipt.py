from datetime import datetime
from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas import receipt as schemas
from domains.shop.services.receipt import receipt_service as actions

receipt_router = APIRouter(prefix="/receipts")


@receipt_router.get(
    "",
    response_model=List[schemas.VanillaReceiptSchema],
)
async def list_receipts(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
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
) -> Any:
    receipts = await actions.list_receipts(
        db=db, skip=skip, limit=limit,
        order_by=order_by, order_direction=order_direction,
        time_from=time_from, time_to=time_to,
        price_from=price_from, price_to=price_to,
        is_refunded=is_refunded, payment_type=payment_type
    )
    return receipts


@receipt_router.post(
    "",
    response_model=schemas.ReceiptSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_receipt(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.ReceiptCreateWithSales
) -> Any:
    receipt = await actions.create_receipt(db=db, data=data, created_by_id=current_user.id)
    return receipt


# @receipt_router.put(
#     "/{id}",
#     response_model=schemas.ReceiptSchema,
#     responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
# )
async def update_receipt(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.ReceiptUpdate,
) -> Any:
    receipt = await actions.update_receipt(db=db, id=id, data=data)
    return receipt


@receipt_router.get(
    "/{id}",
    response_model=schemas.ReceiptSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_receipt(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    receipt = await actions.get_receipt(db=db, id=id)
    return receipt


@receipt_router.delete(
    "/{id}",
    name="refund_all_sold_items",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_receipt(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_receipt(db=db, id=id)
