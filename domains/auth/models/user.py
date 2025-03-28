from sqlalchemy import (
    Column, String, ForeignKey, Boolean, Table, UUID
)
from sqlalchemy.orm import relationship

from db.table import BaseModel, Base

user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id")),
    Column("role_id", UUID, ForeignKey("roles.id"))
)
user_permissions = Table(
    "user_permissions", Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id")),
    Column("permission_id", UUID, ForeignKey("permissions.id"))

)
role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id")),
    Column("permission_id", UUID, ForeignKey("permissions.id"))
)


class User(BaseModel):
    username = Column(String(64), unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    other_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    cellphone = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.username}"

    def get_roles(self) -> list[str]:
        return [role.title for role in self.roles]

    def get_permissions(self) -> list[str]:
        role_permissions = set(
            permission.title for role in self.roles for permission in role.permissions
        )
        permissions = set(permission.title for permission in self.permissions)
        all_permissions = role_permissions.union(permissions)
        return list(all_permissions)
