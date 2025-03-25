from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.schemas import revoked_token as schemas
from domains.auth.services.revoked_token import revoked_token_service as actions

revoked_token_router = APIRouter(prefix="/revoked_tokens")


@revoked_token_router.get(
    "",
    response_model=List[schemas.RevokedTokenSchema],
)
async def list_revoked_tokens(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    revoked_tokens = await actions.list_revoked_tokens(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return revoked_tokens


@revoked_token_router.post(
    "",
    response_model=schemas.RevokedTokenSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        revoked_token_in: schemas.RevokedTokenCreate
) -> Any:
    revoked_token = await actions.create_revoked_token(db=db, revoked_token_in=revoked_token_in)
    return revoked_token


@revoked_token_router.put(
    "/{id}",
    response_model=schemas.RevokedTokenSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        revoked_token_in: schemas.RevokedTokenUpdate,
) -> Any:
    revoked_token = await actions.update_revoked_token(db=db, id=id, revoked_token_in=revoked_token_in)
    return revoked_token


@revoked_token_router.get(
    "/{id}",
    response_model=schemas.RevokedTokenSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    revoked_token = await actions.get_revoked_token(db=db, id=id)
    return revoked_token


@revoked_token_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_revoked_token(db=db, id=id)
