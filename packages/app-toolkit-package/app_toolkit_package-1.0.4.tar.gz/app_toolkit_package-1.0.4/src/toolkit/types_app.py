from collections.abc import Callable
from typing import Annotated, Any, TypeAlias, TypeVar

from aiogram.types import CallbackQuery, Message
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models.base import Base, TypeModel, TypePK  # noqa

# TODO: to sort out

_F = TypeVar("_F", bound=Callable[..., Any])
_TM = TypeVar("_TM")  # , bound=TypeModel)
_AS = TypeVar("_AS", bound=AsyncSession)
_ASM = TypeVar("_ASM", bound=async_sessionmaker)

Predicate: TypeAlias = Callable[..., bool]

JsonType: TypeAlias = dict[str, str]
DictType: TypeAlias = dict[str, Any]
ResponseType: TypeAlias = dict[int, dict[BaseModel, Any]]

# from decimal import Decimal
CurrencyType: TypeAlias = float  # Decimal
NotRequiredStr: TypeAlias = str | None
NonEmptyStr = Annotated[str, Field(min_length=1, max_length=5000)]


# Bot types ===============================================
EventType: TypeAlias = CallbackQuery | Message


# TESTS ====================
TypeFieldsListNone: TypeAlias = list[str] | None
TypeFieldsDict: TypeAlias = dict[str, Any]
TypeResponseJson: TypeAlias = dict | list | None
