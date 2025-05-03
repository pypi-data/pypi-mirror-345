from collections.abc import AsyncGenerator, Callable
from typing import Any

from pydantic import PositiveInt, PostgresDsn, SecretStr
from pydantic_core import MultiHostUrl
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import Pool

from ..types_app import NonEmptyStr
from .base import BaseConf, SettingsConfigDict


class SettingsDB(BaseConf):
    model_config = SettingsConfigDict(env_prefix="DB_")

    DEFAULT: NonEmptyStr = "github_actions"
    SCHEME: NonEmptyStr = "postgresql+asyncpg"
    USER: NonEmptyStr = DEFAULT
    PASSWORD: SecretStr = DEFAULT
    HOST: NonEmptyStr = DEFAULT
    PORT: PositiveInt = 5432
    NAME: NonEmptyStr = DEFAULT

    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme=self.SCHEME,
            username=self.USER,
            password=self.PASSWORD.get_secret_value(),
            host=self.HOST,
            port=self.PORT,
            path=self.NAME,
        )

    def get_dependencies(
        self,
        echo: bool = False,
        expire_on_commit: bool = False,
        autoflush: bool = True,
        poolclass: Pool | None = None,
        # https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
    ) -> tuple[
        AsyncEngine,
        async_sessionmaker[AsyncSession],
        Callable[[], AsyncGenerator[Any, None]],
    ]:
        engine = create_async_engine(
            url=str(self.DATABASE_URI),
            **{"poolclass": poolclass} if poolclass is not None else {},
            echo=echo,
        )

        async_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
        )

        async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
            async with async_session.begin() as s:
                yield s
                assert s.in_transaction()

        return engine, async_session, get_async_session


db_conf = SettingsDB()
engine, async_session, get_async_session = db_conf.get_dependencies(
    echo=True,
    # expire_on_commit=False,
    # autoflush=False,
)


# assert (
#     str(db_conf.DATABASE_URI)
#     == "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres"
# )
