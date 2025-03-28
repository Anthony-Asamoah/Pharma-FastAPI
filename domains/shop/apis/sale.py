from datetime import datetime
from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas import sale as schemas
from domains.shop.services.sale import sale_service as actions

sale_router = APIRouter(prefix="/sales")


@sale_router.get(
    "",
    name="list_all_sold_items",
    response_model=List[schemas.SaleSchema],
)
async def list_sales(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        time_range_min: datetime = None,
        time_range_max: datetime = None,
        is_refunded: bool = False
) -> Any:
    sales = await actions.list_sales(
        db=db,
        skip=skip, limit=limit,
        order_by=order_by, order_direction=order_direction,
        time_range_min=time_range_min, time_range_max=time_range_max,
        is_refunded=is_refunded
    )
    return sales


# @sale_router.post(
#     "",
#     response_model=schemas.SaleSchema,
#     status_code=status.HTTP_201_CREATED,
# )
async def create_sale(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.SaleCreate
) -> Any:
    sale = await actions.create_sale(db=db, data=data)
    return sale


# @sale_router.put(
#     "/{id}",
#     response_model=schemas.SaleSchema,
#     responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
# )
async def update_sale(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.SaleUpdate,
) -> Any:
    sale = await actions.update_sale(db=db, id=id, data=data)
    return sale


@sale_router.get(
    "/{id}",
    name="get_a_sold_item",
    response_model=schemas.SaleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_sale(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    sale = await actions.get_sale(db=db, id=id)
    return sale


@sale_router.delete(
    "/{id}",
    name="refund_an_item",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_sale(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_sale(db=db, id=id)
