from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Permission
class PermissionBase(BaseModel):
    title: Optional[str] = None


# Properties to receive via API on creation
class PermissionCreate(PermissionBase):
    title: str


# Properties to receive via API on update
class PermissionUpdate(PermissionBase):
    pass


# Additional properties to return via API
class PermissionSchema(PermissionBase, BaseSchema):
    pass
