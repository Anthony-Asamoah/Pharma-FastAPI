from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.rbac import check_user_role
from domains.auth.schemas import role as schemas
from domains.auth.services.role import role_service as actions

role_router = APIRouter(prefix="/roles")
allowed_roles = ['SuperAdmin', 'Admin']


@role_router.get(
    "",
    response_model=List[schemas.RoleSchema],
    dependencies=[Depends(check_user_role([*allowed_roles, 'Manager']))],
)
async def list_roles(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    roles = await actions.list_roles(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return roles


@role_router.post(
    "",
    response_model=schemas.RoleSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def create_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        role_in: schemas.RoleCreate
) -> Any:
    role = await actions.create_role(db=db, role_in=role_in)
    return role


@role_router.put(
    "/{id}",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def update_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        role_in: schemas.RoleUpdate,
) -> Any:
    role = await actions.update_role(db=db, id=id, role_in=role_in)
    return role


@role_router.get(
    "/{id}",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def get_role_by_id(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    role = await actions.get_role(db=db, id=id)
    return role


@role_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def delete_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_role(db=db, id=id)


@role_router.put(
    "/{id}/permissions",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def add_permissions_to_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permissions_in: schemas.RolePermissions,
) -> Any:
    role = await actions.get_role(db=db, id=id)
    role = await actions.add_permissions_to_role(db=db, id=role.id, permissions_in=permissions_in)
    return role


@role_router.delete(
    "/{id}/permissions",
    response_model=dict[str, Any],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(allowed_roles))],
)
async def remove_permissions_from_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permissions_in: schemas.RolePermissions,
) -> Any:
    role = await actions.get_role(db=db, id=id)
    role = await actions.remove_permissions_from_role(db=db, id=role.id, permissions_in=permissions_in)
    return role


@role_router.get(
    "/{id}",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    role = await actions.get_role(db=db, id=id)
    return role
