import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from ...test_tools.base_test_fastapi import API_Router, get_header

__all__ = [
    "BASE_URL",
    "generic_async_client",
    "generic_admin_header",
]

BASE_URL = "http://test"


@pytest_asyncio.fixture(scope="session")
async def generic_async_client():
    async def _(app: FastAPI, db_config, testdb_config):
        app.dependency_overrides[db_config.get_async_session] = (
            testdb_config.get_async_session
        )
        API_Router.router = app.router
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=BASE_URL,
        ) as ac:
            yield ac

    return _


@pytest_asyncio.fixture
async def generic_admin_header(async_client):
    async def _(login_data):
        return await get_header(
            client=async_client,
            login_data=login_data,
        )

    return _
