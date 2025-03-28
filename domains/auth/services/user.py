from typing import List, Any, Optional, Literal

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from config.logger import log
from domains.auth.models import User
from domains.auth.oauth.authenticate_user import pwd_context
from domains.auth.repositories.user import user_actions as user_repo
from domains.auth.schemas.permission import PermissionSchema
from domains.auth.schemas.role import RoleSchema
from domains.auth.schemas.user import UserSchema, UserUpdate, UserCreate, ChangePasswordSchema


class UserService:

    def __init__(self):
        self.repo = user_repo

    async def change_password(self, db: Session, user: User, passwords_in: ChangePasswordSchema):
        old_password = passwords_in.old_password.strip()
        new_password = passwords_in.new_password.strip()

        if not new_password: raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide a new valid password",
        )
        if not pwd_context.verify(old_password, user.password): raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect",
        )
        try:
            await self.repo.change_password(db, user, new_password)
        except:
            log.exception("Failed to change password")

        return {"detail": "Password changed successfully"}

    async def list_users(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            is_deleted: bool = False,
    ) -> List[UserSchema]:
        users = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction,
            is_deleted=is_deleted,
        )
        return users

    async def create_user(self, db: Session, *, data: UserCreate) -> UserSchema:
        user = await self.repo.create(db=db, data=data)
        return user

    async def update_user(self, db: Session, *, id: UUID4, data: UserUpdate) -> UserSchema:
        user = await self.repo.get_by_id(db=db, id=id)
        user = await self.repo.update(db=db, db_obj=user, data=data)
        return user

    async def get_user(self, db: Session, *, id: UUID4) -> UserSchema:
        user = await self.repo.get_by_id(db=db, id=id)
        return user

    async def delete_user(self, db: Session, *, id: UUID4, soft=True) -> None:
        await self.repo.delete(db=db, id=id, soft=soft)

    async def get_user_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users

    async def search_users(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users

    async def get_user_by_username(self, db: Session, username: str, silent=True):
        return await self.repo.get_user_by_username(db, username, silent=silent)

    async def get_roles(self, *, db: Session, user_id: UUID4) -> List[RoleSchema]:
        roles = await self.repo.get_all_roles(db=db, user_id=user_id)
        return roles

    async def set_roles(self, db: Session, user_id, role_ids: List[UUID4]) -> Any:
        return await self.repo.set_roles(db, user_id, role_ids)

    async def add_roles(self, db: Session, user_id, role_ids: List[UUID4]) -> Any:
        return await self.repo.add_roles(db, user_id, role_ids)

    async def get_permissions(self, *, db: Session, user_id: UUID4) -> List[PermissionSchema]:
        permissions = await self.repo.get_all_permissions(db=db, user_id=user_id)
        return permissions

    async def get_flattened_permissions(self, *, db: Session, user_id: UUID4) -> List[PermissionSchema]:
        permissions = await self.repo.get_all_permissions(db=db, user_id=user_id, flat=True)
        return permissions

    async def set_permissions(self, db: Session, user_id, permission_ids: List[UUID4]) -> Any:
        return await self.repo.set_permissions(db, user_id, permission_ids)

    async def add_permissions(self, db: Session, user_id, permission_ids: List[UUID4]) -> Any:
        return await self.repo.add_permissions(db, user_id, permission_ids)

    async def remove_permissions(self, db: Session, user_id, permission_ids: List[UUID4]) -> Any:
        return await self.repo.remove_permissions(db, user_id, permission_ids)

    async def remove_roles(self, db: Session, user_id, role_ids: List[UUID4]) -> Any:
        return await self.repo.remove_roles(db, user_id, role_ids)

    async def log_out(self, db: Session, user: User):
        return {"message": "Logged out successfully"}


user_service = UserService()
