from pydantic import PositiveInt, RedisDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import SettingsConfigDict
from redis import asyncio as aioredis  # type: ignore [import]

from ..types_app import NonEmptyStr
from .base import BaseConf


class SettingsRedis(BaseConf):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    SCHEME: NonEmptyStr = "redis"
    HOST: NonEmptyStr = "redis"
    PORT: PositiveInt = 6379
    EXPIRE: PositiveInt = 3600

    @property
    def REDIS_URI(self) -> RedisDsn:
        return MultiHostUrl.build(
            scheme=self.SCHEME,
            host=self.HOST,
            port=self.PORT,
        )

    def get_dependencies(self):
        def get_aioredis() -> aioredis.Redis:
            return aioredis.from_url(
                str(self.REDIS_URI),
                decode_responses=True,
            )

        def get_redis():
            return aioredis.Redis(host=self.HOST, port=self.PORT)

        return get_aioredis, get_redis


redis_conf = SettingsRedis()
get_aioredis, _ = redis_conf.get_dependencies()
