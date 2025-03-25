from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from crud.base_schema import BaseSchema


# RevokedToken
class RevokedTokenBase(BaseModel):
    jti: Optional[str] = None


# Properties to receive via API on creation
class RevokedTokenCreate(RevokedTokenBase):
    jti: str


# Properties to receive via API on update
class RevokedTokenUpdate(RevokedTokenBase):
    pass


class RevokedTokenInDBBase(RevokedTokenBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class RevokedTokenSchema(RevokedTokenBase, BaseSchema):
    pass
