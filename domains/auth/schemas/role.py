from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# Role
class RoleBase(BaseModel):
    title: Optional[str] = None
    default: Optional[bool] = None


# Properties to receive via API on creation
class RoleCreate(RoleBase):
    title: str


# Properties to receive via API on update
class RoleUpdate(RoleBase):
    pass


class RolePermissions(BaseModel):
    permissions_ids: List[UUID4]


class PermissionVanilla(BaseModel):
    id: UUID4
    title: Optional[str] = None


# Additional properties to return via API
class RoleSchema(RoleBase, BaseSchema):
    permissions: List[PermissionVanilla] = []
