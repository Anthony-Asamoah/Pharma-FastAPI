from sqlalchemy import Column, Text

from db.table import BaseModel


class RevokedToken(BaseModel):
    jti = Column(Text)
