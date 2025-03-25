from pydantic import BaseModel

from .user import UserSchema


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    user: UserSchema | None = None
    roles: list[str] | None = None
    permissions: list[str] | None = None
