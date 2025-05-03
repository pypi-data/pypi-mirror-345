# https://docs.sqlalchemy.org/en/20/
import uuid
from typing import Any, TypeAlias

from sqlalchemy import UUID, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped["TypePK"] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    def model_dump(self, *exclude) -> dict[str, Any]:
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in exclude
        }

    def __repr__(self) -> str:
        # args = [f"{k}={repr(v)}" for k, v in self.model_dump().items()]
        args = [f"{k}={v!r}" for k, v in self.model_dump().items()]
        return f"{self.__class__.__name__}({', '.join(args)})"

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.model_dump() == other.model_dump()
        return NotImplemented
        # raise TypeError(f"Objects type mismatch:
        # {type(self)} != {type(other)}")


TypeModel: TypeAlias = type[Base]
TypePK: TypeAlias = uuid.UUID
