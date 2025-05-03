import datetime as dt
import uuid
from collections.abc import Sequence
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from re import Pattern
from types import GeneratorType
from typing import Any

import asyncpg.pgproto.pgproto as asyncpg
from pydantic.networks import AnyUrl, NameEmail
from pydantic.types import SecretBytes, SecretStr


def isoformat(o: dt.date | dt.time) -> str:
    return o.isoformat()


JSON_CONVERT_TABLE = {
    bytes: lambda o: o.decode(),
    dt.date: isoformat,
    dt.datetime: isoformat,
    dt.time: isoformat,
    dt.timedelta: lambda td: td.total_seconds(),
    Decimal: float,
    Enum: lambda o: o.value,
    frozenset: list,
    GeneratorType: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    NameEmail: str,
    Path: str,
    Pattern: lambda o: o.pattern,
    SecretBytes: str,
    SecretStr: str,
    set: list,
    uuid.UUID: str,
    asyncpg.UUID: str,
    AnyUrl: str,
}


def jsonable_converter(entity: dict[str, Any] | Sequence):
    def convert(item: Any):
        t = type(item)
        return JSON_CONVERT_TABLE[t](item) if t in JSON_CONVERT_TABLE else item  # type: ignore [operator]

    if isinstance(entity, dict):
        return {k: convert(v) for k, v in entity.items()}
    if isinstance(entity, (list, tuple, set)):
        return type(entity)(map(convert, entity))
