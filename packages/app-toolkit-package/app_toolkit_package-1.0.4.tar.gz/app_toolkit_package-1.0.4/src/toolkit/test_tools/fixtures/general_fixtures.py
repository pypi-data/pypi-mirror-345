from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.testdb_config import async_session, engine
from ...models.base import Base
from ...types_app import _AS

__all__ = [
    "override_session",
    "init_db",
    "get_test_session",
    "generic_admin",
]


@pytest.fixture
def override_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """General fixture."""
    for module in ("toolkit.config.db_config",):
        monkeypatch.setattr(f"{module}.async_session", async_session)


@pytest_asyncio.fixture
async def init_db(override_session):
    """General fixture."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def get_test_session(init_db) -> AsyncGenerator[None, AsyncSession]:
    """General fixture."""
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def generic_admin(get_test_session: _AS):
    async def _(test_admin_obj):
        get_test_session.add(test_admin_obj)
        await get_test_session.commit()
        await get_test_session.refresh(test_admin_obj)
        return test_admin_obj

    return _
