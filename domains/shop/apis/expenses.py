from datetime import datetime
from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas import expenses as schemas
from domains.shop.services.expenses import expenses_service as actions

expenses_router = APIRouter(prefix="/expenses")


@expenses_router.get(
    "",
    response_model=List[schemas.ExpensesSchema],
)
async def list_expenses(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        search: str = None,
        time_range_min: datetime = None,
        time_range_max: datetime = None,
        price_range_min: float = None,
        price_range_max: float = None,
        is_deleted: bool = None,
) -> Any:
    expense = await actions.list_expenses(
        db=db, skip=skip, limit=limit, search=search, is_deleted=is_deleted,
        order_by=order_by, order_direction=order_direction,
        time_range_min=time_range_min, time_range_max=time_range_max,
        price_range_min=price_range_min, price_range_max=price_range_max,
    )
    return expense


@expenses_router.post(
    "",
    response_model=schemas.ExpensesSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_expenses(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.ExpensesCreate
) -> Any:
    expenses = await actions.create_expenses(db=db, data=data, created_by_id=current_user.id)
    return expenses


@expenses_router.put(
    "/{id}",
    response_model=schemas.ExpensesSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_expenses(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.ExpensesUpdate,
) -> Any:
    expenses = await actions.update_expenses(db=db, id=id, data=data)
    return expenses


@expenses_router.get(
    "/{id}",
    response_model=schemas.ExpensesSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_expenses(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    expenses = await actions.get_expenses(db=db, id=id)
    return expenses


@expenses_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_expenses(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_expenses(db=db, id=id)
