from datetime import datetime

from ..utils.misc_utils import get_time_now
from .base import Base, Mapped, mapped_column


class BaseLog(Base):
    """Лог событий."""

    client_info: Mapped[str]
    at_time: Mapped[datetime] = mapped_column(default=get_time_now)
