import sys
from datetime import datetime
from typing import Union, Dict, Any, List, Optional, Literal

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from config.logger import log
from crud.base_repository import BaseCRUDRepository
from domains.auth.models.permission import Permission
from domains.auth.models.role import Role
from domains.auth.models.user import User
from domains.auth.schemas.user import (
    UserCreate, UserUpdate
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        from domains.auth.utils.authenticate_user import pwd_context
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        from domains.auth.utils.authenticate_user import pwd_context
        return pwd_context.hash(password)


class CRUDUser(BaseCRUDRepository[User, UserCreate, UserUpdate]):
    async def get_user_by_username(self, db: Session, username: str, silent=True) -> User | bool:
        user = await self.get_one(db=db, silent=silent, username=username)
        if not user: return False
        return user

    async def create(self, db: Session, *, data: UserCreate) -> User:

        data_data = jsonable_encoder(data)

        # hash password
        data_data["password"] = Hasher.get_password_hash(data_data["password"])

        # existing_user check
        existing_user = await self.get_user_by_username(db, username=data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username {existing_user.username} already taken"
            )

        # related object ids m2m
        role_ids = data_data.pop("role_ids", [])
        permission_ids = data_data.pop("permission_ids", [])

        db_obj = User(**data_data)

        try:
            if role_ids:
                roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
                if roles:
                    db_obj.roles.extend(roles)
                    db.add(db_obj)

            if permission_ids:
                permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
                if permissions:
                    db_obj.permissions.extend(permissions)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="{}".format(sys.exc_info()[1]))

        except:
            db.rollback()
            log.exception(f"Failed to create user.")
            raise await http_500_exc_internal_server_error()

    async def update(
            self,
            db: Session,
            *,
            db_obj: User,
            data: Union[UserUpdate, Dict[str, Any]]
    ) -> Any:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)

        # related object ids m2m
        role_ids = update_data.pop("role_ids", [])
        permission_ids = update_data.pop("permission_ids", [])

        try:
            # role check
            if role_ids:
                roles = db.query(Role).filter(
                    Role.id.in_(role_ids)).all()
                if roles:
                    for role in roles:
                        # add if not existing
                        if not role in User.roles:
                            db_obj.roles.append(role)

            # permissions check
            if permission_ids:
                permissions = db.query(Permission).filter(
                    Permission.id.in_(permission_ids)).all()
                if permissions:
                    for permission in permissions:
                        if not permission in User.permissions:
                            db_obj.permissions.append(permission)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="{}".format(sys.exc_info()[1]))

        except:
            db.rollback()
            log.exception("Failed to update user.")
            raise await http_500_exc_internal_server_error()

    async def change_password(self, db: Session, user: User, new_password: str):
        user.password = Hasher.get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    async def add_roles(self, db: Session, user_id: UUID4, role_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.role import role_actions
        roles = await role_actions.get_many_by_ids(db=db, ids=role_ids)
        if roles:
            for role in roles:
                if not role in user.roles:
                    user.roles.append(role)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    async def set_roles(self, db: Session, user_id, role_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.role import role_actions
        roles = await role_actions.get_many_by_ids(db=db, ids=role_ids)
        user.roles = roles
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    async def remove_roles(self, db: Session, user_id, role_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.role import role_actions
        roles = await role_actions.get_many_by_ids(db=db, ids=role_ids)
        if roles:
            for role in roles:
                if role in user.roles:
                    user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user

    async def add_permissions(self, db: Session, user_id, permission_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.permission import permission_actions
        permissions = await permission_actions.get_many_by_ids(db=db, ids=permission_ids)

        if permissions:
            for permission in permissions:
                if not permission in user.permissions:
                    user.roles.append(permission)
            db.commit()
            db.refresh(user)
        return user

    async def set_permissions(self, db: Session, user_id, permission_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.permission import permission_actions
        permissions = await permission_actions.get_many_by_ids(db=db, ids=permission_ids)

        user.permissions = permissions
        db.commit()
        db.refresh(user)
        return user

    async def remove_permissions(self, db: Session, user_id, permission_ids: List[UUID4]):
        user = await self.get_by_id(db, id=user_id)

        from domains.auth.repositories.permission import permission_actions
        permissions = await permission_actions.get_many_by_ids(db=db, ids=permission_ids)

        if permissions:
            for permission in permissions:
                if permission in user.permissions:
                    user.permissions.remove(permission)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    async def get_all_permissions(self, db: Session, user_id: UUID4):
        user = await self.get_by_id(db, id=user_id)
        return user.permissions

    async def has_permission(self, db: Session, user_id, permission_name):
        """Checks if a user has a specific permission directly or through roles."""

        user = await self.get_by_id(db, id=user_id)
        return (permission_name in [p.title for p in User.permissions] or
                any(permission_name in [p.title for p in role.permissions] for role in user.roles))

    async def get_all_roles(self, db: Session, user_id: UUID4):
        user = await self.get_by_id(db, id=user_id)
        return user.roles

    async def has_role(self, db: Session, user_id, role_name):
        """Checks if a user has a specific role directly or through roles."""

        user = await self.get_by_id(db, id=user_id)
        return (role_name in [r.title for r in User.roles] or
                any(role_name in [r.title for r in role.roles] for role in user.roles))

    async def get_all(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            is_deleted: bool = None,
            is_suspended: bool = None,
            search: str = None,
    ) -> List[User]:
        query = db.query(User)
        try:
            if search: query = query.filter(or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
            ))
            if is_deleted is not None: query = query.filter(User.deleted_at.isnot(None) == is_deleted)
            if is_suspended is not None: query = query.filter(User.is_active != is_suspended)

            if time_range_min: query = query.filter(User.created_at >= time_range_min)
            if time_range_max: query = query.filter(User.created_at <= time_range_max)

            query = await self._get_ordering(query, order_by)
            results = query.offset(skip).limit(limit).all()
            return results
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {User.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {User.__name__}")
            raise await http_500_exc_internal_server_error()


user_actions = CRUDUser(User)
