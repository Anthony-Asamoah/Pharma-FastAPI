from functools import wraps

from fastapi import Depends, status, HTTPException

from domains.auth.models.user import User
from domains.auth.oauth.get_current_active_user import get_current_active_user
from domains.auth.oauth.get_current_user import get_current_user


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
