from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.schemas import revoked_token as schemas
from domains.auth.services.revoked_token import revoked_token_service as actions
from domains.auth.utils import get_current_user
from domains.auth.utils.rbac import check_user_role

revoked_token_router = APIRouter(prefix="/revoked_tokens")
allowed_roles = ["SuperAdmin", "Admin"]


@revoked_token_router.get(
    "",
    response_model=List[schemas.RevokedTokenSchema],
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def list_revoked_tokens(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[List[str]] = None,
) -> Any:
    revoked_tokens = await actions.list_revoked_tokens(
        db=db, skip=skip, limit=limit, order_by=order_by
    )
    return revoked_tokens


@revoked_token_router.post(
    "",
    response_model=schemas.RevokedTokenSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_user_role(allowed_roles))],
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
    dependencies=[Depends(check_user_role(allowed_roles))],
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
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def get_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    revoked_token = await actions.get_revoked_token_by_id(db=db, id=id)
    return revoked_token


@revoked_token_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def delete_revoked_token(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_revoked_token(db=db, id=id)
