from ..types_app import NotRequiredStr
from .base import Base, Mapped, mapped_column


class BaseUser(Base):
    __abstract__ = True

    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    first_name: Mapped[NotRequiredStr]
    last_name: Mapped[NotRequiredStr]
    phone_number: Mapped[NotRequiredStr]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
