from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from db.table import BaseModel


class Role(BaseModel):
    title = Column(String, nullable=False, unique=True)
    default = Column(Boolean, nullable=False, default=False)
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __str__(self):
        return self.title
