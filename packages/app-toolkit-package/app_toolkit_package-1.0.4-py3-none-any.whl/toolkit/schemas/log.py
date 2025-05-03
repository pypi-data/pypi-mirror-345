from datetime import datetime

from ..schemas.base import Base
from ..types_app import NonEmptyStr


class BaseLog(Base):
    """Лог событий."""

    client_info: NonEmptyStr
    at_time: datetime
