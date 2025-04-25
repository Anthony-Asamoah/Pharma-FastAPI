from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.schemas import permission as schemas
from domains.auth.services.permission import permission_service as actions
from domains.auth.utils import get_current_user
from domains.auth.utils.rbac import check_user_role

permission_router = APIRouter(prefix="/permissions")
allowed_roles = ['SuperAdmin', 'Admin']


@permission_router.get(
    "",
    response_model=List[schemas.PermissionSchema],
    dependencies=[Depends(check_user_role([*allowed_roles, 'Manager']))],
)
async def list_permissions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[List[str]] = None,
) -> Any:
    permissions = await actions.list_permissions(
        db=db, skip=skip, limit=limit, order_by=order_by
    )
    return permissions


@permission_router.post(
    "",
    response_model=schemas.PermissionSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def create_permission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        permission_in: schemas.PermissionCreate
) -> Any:
    permission = await actions.create_permission(db=db, permission_in=permission_in)
    return permission


@permission_router.put(
    "/{id}",
    response_model=schemas.PermissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def update_permission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permission_in: schemas.PermissionUpdate,
) -> Any:
    permission = await actions.update_permission(db=db, id=id, permission_in=permission_in)
    return permission


@permission_router.get(
    "/{id}",
    response_model=schemas.PermissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def get_permission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    permission = await actions.get_permission(db=db, id=id)
    return permission


@permission_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def delete_permission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_permission(db=db, id=id)
