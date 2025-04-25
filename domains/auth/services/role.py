from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.auth.models import Role
from domains.auth.repositories.role import role_actions as role_repo
from domains.auth.schemas.role import RoleSchema, RoleUpdate, RoleCreate


class RoleService:

    def __init__(self):
        self.repo = role_repo

    async def get_by_title(self, db: Session, name: str, silent: bool = True) -> Optional[Role]:
        role = await self.repo.get_one(db=db, silent=silent, name=name)
        return role

    async def list_roles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            search: str = None,
    ) -> List[RoleSchema]:
        roles =  await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, title=search
        )
        return roles

    async def create_role(self, db: Session, *, role_in: RoleCreate) -> RoleSchema:
        role = await self.repo.create(db=db, data=role_in)
        return role

    async def update_role(self, db: Session, *, id: UUID4, role_in: RoleUpdate) -> RoleSchema:
        role = await self.repo.get_by_id(db=db, id=id)
        role = await self.repo.update(db=db, db_obj=role, data=role_in)
        return role

    async def get_role(self, db: Session, *, id: UUID4) -> RoleSchema:
        role = await self.repo.get_by_id(db=db, id=id)
        return role

    async def delete_role(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_role_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[RoleSchema]:
        roles = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return roles

    async def search_roles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[RoleSchema]:
        roles = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return roles


role_service = RoleService()
