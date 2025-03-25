from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Permission(BaseModel):
    title = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary="user_permissions", back_populates="permissions")
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __str__(self):
        return self.title
