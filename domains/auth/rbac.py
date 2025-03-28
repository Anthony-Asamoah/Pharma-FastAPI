from functools import wraps
from typing import Annotated

from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.user import User
from domains.auth.oauth.get_current_active_user import get_current_active_user
from domains.auth.oauth.get_current_user import get_current_user
from domains.auth.services.user import user_service


def check_user_role(roles: list[str]):
    async def role_check(
            current_active_user: Annotated[User, Depends(get_current_user)],
            db: Session = Depends(get_db)
    ):
        user_roles = await user_service.get_roles(db=db, user_id=current_active_user.id)
        roles_names = [role.title for role in user_roles]

        user_roles = set(roles) & set(roles_names)
        if not user_roles: raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required permissions to perform this action"
        )
        return user_roles

    return role_check


class RoleChecker:
    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> bool:
        user_roles = user.get_roles()
        for role in self.required_roles:
            if role not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Permissions'
                )
        return True


class PermissionChecker:

    def __init__(self, required_permissions: list[str]) -> None:
        self.required_permissions = required_permissions

    def __call__(self, user: User = Depends(get_current_user)) -> bool:
        user_permissions = user.get_permissions()
        for r_perm in self.required_permissions:
            if r_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Permissions'
                )
        return True


def auth_check(required_roles):
    def decorator_auth(func):
        @wraps(func)
        def wrapper_auth(*args, user=Depends(get_current_active_user), **kwargs):
            if not set(required_roles) & set(user.roles):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Permissions'
                )
            return func(*args, **kwargs)

        return wrapper_auth

    return decorator_auth
