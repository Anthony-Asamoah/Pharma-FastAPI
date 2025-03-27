from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas import stock as schemas
from domains.shop.services.stock import stock_service as actions

stock_router = APIRouter(prefix="/stock")


@stock_router.get(
    "",
    response_model=List[schemas.StockSchema],
)
async def list_stocks(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    stocks = await actions.list_stocks(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return stocks


@stock_router.post(
    "",
    response_model=schemas.StockSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_stock(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.StockCreate
) -> Any:
    stock = await actions.create_stock(db=db, data=data, created_by_id=current_user.id)
    return stock


@stock_router.put(
    "/{id}",
    response_model=schemas.StockSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_stock(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.StockUpdate,
) -> Any:
    stock = await actions.update_stock(db=db, id=id, data=data)
    return stock


@stock_router.get(
    "/{id}",
    response_model=schemas.StockSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_stock(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    stock = await actions.get_stock(db=db, id=id)
    return stock


@stock_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_stock(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        soft=True
) -> None:
    await actions.delete_stock(db=db, id=id, soft=soft)
