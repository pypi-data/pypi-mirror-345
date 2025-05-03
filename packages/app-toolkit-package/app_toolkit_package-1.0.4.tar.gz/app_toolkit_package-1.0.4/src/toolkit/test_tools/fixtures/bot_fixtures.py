import pytest
from aiogram import Bot, Router

from ...api.bot.utils import get_dispatcher

__all__ = [
    "generic_bot",
    "generic_dispatcher",
]


@pytest.fixture(scope="session")
def generic_bot():
    def _(token: str):
        return Bot(token=token)

    return _


@pytest.fixture(scope="session")
def generic_dispatcher():
    def _(*routers: Router, **dependencies):
        return get_dispatcher(*routers, **dependencies)

    return _
