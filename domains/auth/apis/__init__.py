from fastapi import APIRouter

from .change_password import change_password_router
from .login import login_router
from .logout import logout_router
from .permission import permission_router
from .refresh_token import refresh_token_router
from .revoked_token import revoked_token_router
from .role import role_router
from .user import user_router

auth_routers = APIRouter()
auth_routers.include_router(login_router, tags=["AUTH"])
auth_routers.include_router(logout_router, tags=["AUTH"])
auth_routers.include_router(refresh_token_router, tags=["AUTH"])
auth_routers.include_router(permission_router, tags=["AUTH PERMISSIONS"])
auth_routers.include_router(role_router, tags=["AUTH ROLES"])
auth_routers.include_router(revoked_token_router, tags=["AUTH REVOKED TOKENS"])
auth_routers.include_router(user_router, tags=["USERS"])
auth_routers.include_router(change_password_router, tags=["CHANGE PASSWORD"])
