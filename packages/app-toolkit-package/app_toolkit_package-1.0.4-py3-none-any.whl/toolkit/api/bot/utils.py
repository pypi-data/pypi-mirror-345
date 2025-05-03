from collections.abc import Coroutine
from typing import Any

from aiogram import Dispatcher, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...types_app import EventType


async def try_return(
    return_coro: Coroutine,
    possible_exception,  # : BaseCustomException,
) -> Any:
    try:
        return await return_coro
    except possible_exception as e:
        return e.msg


def get_dispatcher(*routers: Router, **dependencies) -> Dispatcher:
    """Creates dispatcher and includes the routers.

    Arguments:
      *routers - routers from the handlers
      **dependencies - arbitrary dependencies (like DB session)  necessary for bot application

    Returns:
        Dispatcher:
    """
    dp = Dispatcher(**dependencies)
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_routers(*routers)
    return dp


def get_username(event: EventType) -> str:
    """Returns user full name."""
    return event.from_user.full_name


def get_markup(*buttons: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Generates keyboard from the buttons.

    Arguments:
        *buttons: list of rows. Each row is the tuple of button(s), each button described by tuple[str, str].

    Returns:
        InlineKeyboardMarkup:
    """
    kb_builder = InlineKeyboardBuilder()
    for button in buttons:
        bts = [
            InlineKeyboardButton(text=text, callback_data=callback_data)
            for text, callback_data in button
        ]
        kb_builder.row(*bts)
    return kb_builder.as_markup()
