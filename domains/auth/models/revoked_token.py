from sqlalchemy import Column, String

from db.table import BaseModel


class RevokedToken(BaseModel):
    jti = Column(String)
