from typing import List

from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_repository import BaseCRUDRepository
from domains.auth.models.permission import Permission
from domains.auth.schemas.permission import (
    PermissionCreate, PermissionUpdate
)


class CRUDPermission(BaseCRUDRepository[Permission, PermissionCreate, PermissionUpdate]):
    async def get_all_by_user_id(
            self, db: Session, user_id: UUID4, skip: int = 0, limit: int = 100
    ) -> List[Permission]:
        return await self.get_by_filters(db=db, user_id=user_id, skip=skip, limit=limit)


permission_actions = CRUDPermission(Permission)
