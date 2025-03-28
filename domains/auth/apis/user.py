from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.schemas import user as schemas
from domains.auth.schemas.permission import PermissionSchema
from domains.auth.schemas.role import RoleSchema
from domains.auth.services.user import user_service as actions

user_router = APIRouter(prefix="/users")


@user_router.get(
    "",
    response_model=List[schemas.UserSchema],
)
async def list_users(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        is_deleted: bool = False,
) -> Any:
    users = await actions.list_users(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, is_deleted=is_deleted,
    )
    return users


@user_router.post(
    "",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.UserCreate
) -> Any:
    user = await actions.create_user(db=db, data=data)
    return user


@user_router.put(
    "/{id}",
    response_model=schemas.UserSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.UserUpdate,
) -> Any:
    user = await actions.update_user(db=db, id=id, data=data)
    return user


@user_router.get(
    "/{id}",
    response_model=schemas.UserSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    user = await actions.get_user(db=db, id=id)
    return user


@user_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_user(db=db, id=id)


@user_router.get(
    "/{id}/roles",
    response_model=List[RoleSchema],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_user_roles(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    return await actions.get_roles(db=db, user_id=id)


@user_router.post(
    "/{id}/roles",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def set_roles_on_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        role_ids: schemas.UserRole
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.set_roles(db, user.id, role_ids.role_ids)
    return user


@user_router.patch(
    "/{id}/roles",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_role_to_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        role_ids: schemas.UserRole
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.add_roles(db, user.id, role_ids.role_ids)
    return user


@user_router.delete(
    "/{id}/roles",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def remove_role_from_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        role_ids: schemas.UserRole
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.remove_roles(db, user.id, role_ids.role_ids)
    return user


@user_router.get(
    "/{id}/permissions",
    response_model=List[PermissionSchema],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_user_permissions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    return await actions.get_permissions(db=db, user_id=id)


@user_router.post(
    "/{id}/permissions",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def set_permissions_on_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permission_ids: schemas.UserPermission
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.set_permissions(db, user.id, permission_ids.permission_ids)
    return user


@user_router.patch(
    "/{id}/permissions",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_permission_to_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permission_ids: schemas.UserPermission
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.add_permissions(db, user.id, permission_ids.permission_ids)
    return user


@user_router.delete(
    "/{id}/permissions",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def remove_permission_from_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        permission_ids: schemas.UserPermission
) -> Any:
    user = await actions.get_user(db=db, id=id)
    user = await actions.remove_permissions(db, user.id, permission_ids.permission_ids)
    return user
