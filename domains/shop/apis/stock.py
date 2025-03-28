from datetime import date
from typing import Any, List, Literal

import pendulum
from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.rbac import check_user_role
from domains.shop.schemas import stock as schemas
from domains.shop.services.stock import stock_service as actions

stock_router = APIRouter(prefix="/stock")
allowed_roles = ["SuperAdmin", "Admin", "Manager", "Supervisor"]


@stock_router.get(
    "",
    description="Get a list of available stock in alphabetical order",
    response_model=List[schemas.VanillaStockSchema],
)
async def list_stocks(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = "name",
        order_direction: Literal['asc', 'desc'] = 'asc',
        search: str = None,
        quantity_min: int = 1,
        quantity_max: int = None,
        expiry_date_min: date = pendulum.now().date(),
        expiry_date_max: date = None,
        selling_price_min: float = None,
        selling_price_max: float = None,
) -> Any:
    stocks = await actions.list_stocks(
        db=db, skip=skip, limit=limit, search=search,
        order_by=order_by, order_direction=order_direction,
        quantity_min=quantity_min, quantity_max=quantity_max,
        expiry_date_min=expiry_date_min, expiry_date_max=expiry_date_max,
        selling_price_min=selling_price_min, selling_price_max=selling_price_max,
    )
    return stocks


@stock_router.post(
    "",
    response_model=schemas.StockSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_user_role(allowed_roles))],
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
    dependencies=[Depends(check_user_role(allowed_roles))],
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


@stock_router.get(
    "/ref/{id}",
    response_model=schemas.StockSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_stock_by_reference(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: str
) -> Any:
    stock = await actions.get_by_reference(db=db, ref=id)
    return stock


@stock_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def delete_stock(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        soft: bool = True
) -> None:
    await actions.delete_stock(db=db, id=id, soft=soft)
