from datetime import datetime
from typing import List, Any, Optional

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from config.logger import log
from domains.auth.models import User
from domains.auth.utils.authenticate_user import pwd_context
from domains.auth.repositories.user import user_actions as user_repo
from domains.auth.schemas.permission import PermissionSchema
from domains.auth.schemas.revoked_token import RevokedTokenCreate
from domains.auth.schemas.role import RoleSchema
from domains.auth.schemas.user import UserSchema, UserUpdate, UserCreate, ChangePasswordSchema
from domains.auth.services.revoked_token import revoked_token_service
from domains.auth.services.role import role_service


class UserService:

    def __init__(self):
        self.repo = user_repo

    async def activate_user(self, db: Session, id: int) -> Optional[User]:
        user = await self.repo.get_by_id(db=db, id=id)
        payload = dict(
            is_active=True,
            deleted_at=None
        )
        return await self.repo.update(db=db, db_obj=user, data=payload)

    async def change_password(self, db: Session, user_id: User, passwords_in: ChangePasswordSchema):
        user = await self.repo.get_by_id(db=db, id=user_id)

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
            order_by: Optional[List[str]] = None,
            search: str = None,
            is_deleted: bool = False,
            is_suspended: bool = False,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
    ) -> List[UserSchema]:
        users = await self.repo.get_all(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            order_by=order_by,
            is_deleted=is_deleted,
            is_suspended=is_suspended,
            time_range_min=time_range_min,
            time_range_max=time_range_max,
        )
        return users

    async def create_user(self, db: Session, *, data: UserCreate) -> UserSchema:
        user = await self.repo.create(db=db, data=data)
        # assign default roles
        roles = await role_service.get_role_by_keywords(db=db,  default=True, is_deleted=None)
        await self.add_roles(db=db, user_id=user.id, role_ids=[role.id for role in roles])
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
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return users

    async def search_users(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
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

    async def logout(self, db: Session, *, token: str):
        await revoked_token_service.create_revoked_token(db=db, revoked_token_in=RevokedTokenCreate(jti=token))
        return {"message": "Logged out successfully"}


user_service = UserService()
