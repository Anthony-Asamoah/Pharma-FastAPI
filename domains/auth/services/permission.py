from typing import List, Optional, Literal

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.auth.repositories.permission import permission_actions as permission_repo
from domains.auth.schemas.permission import PermissionSchema, PermissionUpdate, PermissionCreate
from domains.auth.services.user import user_service


class PermissionService:

    def __init__(self):
        self.repo = permission_repo

    async def get_all_permissions_by_user_id(
            self, *, db: Session, user_id: UUID4, skip: int = 0, limit: int = 100
    ) -> List[PermissionSchema]:
        # todo: refactor method appropriately
        permissions = await user_service.get_all_permissions(db=db, id=user_id)
        return permissions

    async def list_permissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return permissions

    async def create_permission(self, db: Session, *, permission_in: PermissionCreate) -> PermissionSchema:
        permission = await self.repo.create(db=db, data=permission_in)
        return permission

    async def update_permission(self, db: Session, *, id: UUID4, permission_in: PermissionUpdate) -> PermissionSchema:
        permission = await self.repo.get_by_id(db=db, id=id)
        permission = await self.repo.update(db=db, db_obj=permission, data=permission_in)
        return permission

    async def get_permission(self, db: Session, *, id: UUID4) -> PermissionSchema:
        permission = await self.repo.get_by_id(db=db, id=id)
        return permission

    async def delete_permission(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_permission_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return permissions

    async def search_permissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return permissions


permission_service = PermissionService()
