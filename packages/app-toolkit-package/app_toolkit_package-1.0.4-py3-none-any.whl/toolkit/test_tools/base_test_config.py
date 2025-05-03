import re
from collections.abc import AsyncGenerator
from typing import Any

from pydantic_settings import BaseSettings
from redis.asyncio import Redis  # type: ignore [import]
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..config.bot_config import TEST_TOKEN
from .utils import assert_equal, assert_isinstance

__all__ = [
    "BaseTest_Config",
    "BaseTest_BotConfig",
    "BaseTest_DBConfig",
    "BaseTest_RedisConfig",
]


class BaseTest_Config:
    """
    Attributes:
        module - module imported from config as below:
    ```
    from src.config import db_config, testdb_config
    ```
    """

    module: Any
    conf_name: str
    conf_fields: dict[str, Any] = {}

    def get_attr(self, attr_name: str):
        attr = getattr(self.module, attr_name, None)
        assert attr is not None
        return attr

    def test__conf(self):
        conf = self.get_attr(self.conf_name)
        assert_isinstance(conf, BaseSettings)
        for field, value in self.conf_fields.items():
            assert_equal(getattr(conf, field, None), value)


class BaseTest_DBConfig(BaseTest_Config):
    conf_name = "db_conf"

    def test__engine(self):
        engine = self.get_attr("engine")
        assert_isinstance(engine, AsyncEngine)

    async def test__async_session(self):
        async_session = self.get_attr("async_session")
        assert_isinstance(async_session, async_sessionmaker)
        async with async_session.begin() as s:
            assert_isinstance(s, AsyncSession)
            assert s.in_transaction()

    async def test__get_async_session(self):
        get_async_session = self.get_attr("get_async_session")()
        assert_isinstance(get_async_session, AsyncGenerator)
        async for s in get_async_session:
            assert_isinstance(s, AsyncSession)
            assert s.in_transaction()


class BaseTest_RedisConfig(BaseTest_Config):
    conf_name = "redis_conf"

    def test__get_aioredis(self):
        aioredis = self.get_attr("get_aioredis")
        assert_isinstance(aioredis(), Redis)


class BaseTest_BotConfig(BaseTest_Config):
    conf_name = "bot_conf"

    def test__bot_token(self) -> None:
        bot_conf = self.get_attr(self.conf_name)
        for s in (TEST_TOKEN, bot_conf.token.get_secret_value()):
            assert (
                re.match(
                    pattern=r"^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$",
                    string=s,
                )
                is not None
            )
