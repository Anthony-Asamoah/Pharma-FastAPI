from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.auth.repositories.permission import permission_actions as permission_repo
from domains.auth.schemas.permission import PermissionSchema, PermissionUpdate, PermissionCreate


class PermissionService:

    def __init__(self):
        self.repo = permission_repo

    async def get_all_permissions_by_user_id(
            self, *, db: Session, user_id: UUID4, skip: int = 0, limit: int = 100
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_all_by_user_id(db=db, user_id=user_id, skip=skip, limit=limit)
        return permissions

    async def list_permissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by
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
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return permissions

    async def search_permissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[PermissionSchema]:
        permissions = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return permissions


permission_service = PermissionService()
