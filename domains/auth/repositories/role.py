from pydantic import UUID4
from sqlalchemy.orm import Session

from config.logger import log
from crud.base_repository import BaseCRUDRepository
from domains.auth.models import Permission, User
from domains.auth.models.role import Role
from domains.auth.schemas.role import (
    RoleCreate, RoleUpdate
)
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class CRUDRole(BaseCRUDRepository[Role, RoleCreate, RoleUpdate]):

    async def get_all_by_user_id(self, db: Session, user_id: UUID4, skip: int = 0, limit: int = 100) -> list[Role]:
        roles = (
            db.query(self.model)
            .join(self.model.users)
            .filter(User.id == user_id)
            .limit(limit)
            .offset(skip)
            .all()
        )
        return roles

    async def add_permissions_to_role(self, db, db_obj, permission_ids):
        try:
            role = db_obj
            permissions = db.query(Permission).filter(
                Permission.id.in_(list(permission_ids))).all()
            if permissions:
                for permission in permissions:
                    if not permission in role.permissions:
                        role.permissions.append(permission)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except:
            db.rollback()
            log.exception("Failed to add permissions to role")
            raise await http_500_exc_internal_server_error()

    async def remove_permissions_from_role(self, db, db_obj, permission_ids):
        try:
            role = db_obj
            permissions = db.query(Permission).filter(
                Permission.id.in_(permission_ids)).all()
            if permissions:
                for permission in permissions:
                    if permission in role.permissions:
                        role.permissions.remove(permission)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except:
            db.rollback()
            log.exception("Failed to remove permissions from role")
            raise await http_500_exc_internal_server_error()


role_actions = CRUDRole(Role)
