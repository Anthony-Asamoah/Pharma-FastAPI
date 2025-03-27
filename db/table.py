import typing
import typing as t
from functools import reduce
from uuid import uuid4

import inflect
import pendulum
import sqlalchemy
from sqlalchemy import DateTime, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import DeclarativeBase, declared_attr


class DBTable(DeclarativeBase):
    metadata: sqlalchemy.MetaData = sqlalchemy.MetaData()  # type: ignore


Base: typing.Type[DeclarativeBase] = DBTable
class_registry: t.Dict = {}


def change_case(str):
    return reduce(lambda x, y: x + ('_' if y.isupper() else '') + y, str).lower()


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        camel_check = change_case(self.__name__)
        p = inflect.engine()
        return p.plural(camel_check.lower())


class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        default=pendulum.now,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=pendulum.now,
        onupdate=pendulum.now,
        nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        if self.deleted_at is None: return False
        return True
