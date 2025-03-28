from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema
from domains.auth.schemas.permission import PermissionSchema
from domains.auth.schemas.role import RoleSchema


# User
class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    cellphone: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    first_name: str
    last_name: str
    password: str


class ChangePasswordSchema(BaseModel):
    user_id: Optional[UUID4] = None
    old_password: str
    new_password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


# Additional properties to return via API
class UserSchema(UserBase, BaseSchema):
    roles: Optional[List[RoleSchema]] = []
    permissions: Optional[List[PermissionSchema]] = []


class UserRole(BaseModel):
    role_ids: List[UUID4]


class UserPermission(BaseModel):
    permission_ids: List[UUID4]
