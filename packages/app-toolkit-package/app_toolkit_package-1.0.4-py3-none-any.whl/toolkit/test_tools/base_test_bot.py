from datetime import datetime as dt
from types import MethodType
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StateType
from aiogram.types import (
    CallbackQuery,
    Chat,
    DateTime,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)
from pytest import MonkeyPatch

from ..test_tools.mixins import setup_db
from ..test_tools.utils import assert_equal, find_in_stack, mock
from ..types_app import _AS, _F

ID = 1


def get_chat(
    id: int = ID,
    type: str = "chat",
    **kwargs,
) -> Chat:
    return Chat(id=id, type=type, **kwargs)


def get_user(
    id: int = ID,
    is_bot: bool = False,
    first_name: str = "first_name",
    last_name: str = "last_name",
    username: str = "username",
    **kwargs,
) -> User:
    return User(
        id=id,
        is_bot=is_bot,
        first_name=first_name,
        last_name=last_name,
        username=username,
        **kwargs,
    )


def get_message(
    message_id: int = ID,
    date: DateTime | None = None,
    chat: Chat | None = None,
    from_user: User | None = None,
    text: str = "Test message text",
    **kwargs,
) -> Message:
    return Message(
        message_id=message_id,
        date=date or dt.now(),
        chat=chat or get_chat(),
        from_user=from_user or get_user(),
        text=text,
        **kwargs,
    )


def get_callback(
    id: int = ID,
    from_user: User | None = None,
    chat_instance: str = "chat_instance",
    message: Message | None = None,
    data: str | None = None,
    **kwargs,
) -> CallbackQuery:
    return CallbackQuery(
        id=str(id),
        from_user=from_user or get_user(),
        chat_instance=chat_instance,
        message=message or get_message(),
        data=data,
        **kwargs,
    )


def get_update(
    update_id: int = ID,
    event: Message | CallbackQuery | None = None,
    **kwargs,
) -> Update:
    if isinstance(event, Message):
        return Update(update_id=update_id, message=event, **kwargs)
    return Update(update_id=update_id, callback_query=event, **kwargs)


class StateMixin:
    fsm_context: FSMContext
    current_state: StateType = None
    current_state_data: dict[str, Any] | None = None
    expected_state: StateType = None
    expected_state_data: dict[str, Any] = {}

    async def setup_state(self, dispatcher: Dispatcher, bot: Bot) -> None:
        self.fsm_context = dispatcher.fsm.get_context(
            bot=bot,
            chat_id=get_chat().id,
            user_id=get_user().id,
        )
        if self.current_state is not None:
            await self.fsm_context.set_state(self.current_state)
        if self.current_state_data is not None:
            await self.fsm_context.set_data(self.current_state_data)

    async def check_state(self):
        assert_equal(await self.fsm_context.get_state(), self.expected_state)
        assert_equal(await self.fsm_context.get_data(), self.expected_state_data)


class BaseTest_Bot:
    update: Update | None = None
    # mocking ===============================
    handler_send_method: str | None = None
    """Aiogram method sending the message, will be mocked."""
    funcs_to_mock: tuple[tuple] | None = None
    """Please, provide data as follows: (module: object | str, func: _F, mock_func: _F | None)."""
    _mock_counter: int = 0
    # expected values from bot =========================
    expected_mock_counter: int = 0
    expected_handler: _F | None = None  # type: ignore [valid-type]
    expected_text: str = "Not Implemented"
    expected_reply_markup: InlineKeyboardMarkup | None = None

    # MOCKS ====================================================================
    async def _message_mock(self, *args, **kwargs) -> Message:
        if args:
            assert_equal(args[0], self.expected_text)
        if kwargs:
            # assert_equal(kwargs.get("text", self.expected_text), self.expected_text)
            assert_equal(kwargs.get("text"), self.expected_text)
            assert_equal(kwargs.get("reply_markup"), self.expected_reply_markup)
        if self.expected_handler is not None:
            find_in_stack(self.expected_handler.__name__)
        self._mock_counter += 1
        return get_message()

    async def dummy_mock(self, *args, **kwargs) -> None:
        self._mock_counter += 1

    async def setup(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr("aiogram.types.CallbackQuery.answer", self.dummy_mock)
        monkeypatch.setattr(self.handler_send_method, self._message_mock)
        for module, func, *remain in self.funcs_to_mock or []:
            mock(
                monkeypatch=monkeypatch,
                module=module,
                func=func,
                mock_func=MethodType(remain[0], self) if remain else self.dummy_mock,
            )

    # TESTS ========================================================
    async def test__router(
        self,
        get_test_session: _AS,
        monkeypatch: MonkeyPatch,
        dispatcher: Dispatcher,
        bot: Bot,
    ):
        # ARRANGE ========================
        await self.setup(monkeypatch)
        await setup_db(self, get_test_session)
        if hasattr(self, "setup_state"):
            await self.setup_state(dispatcher, bot)
        # ACT ============================
        await dispatcher.feed_update(bot, self.update)
        # ASSERT =========================
        assert_equal(self._mock_counter, self.expected_mock_counter)
        if hasattr(self, "check_state"):
            await self.check_state()
        # TODO: check DB ?


class BaseTest_MessageUpdate(BaseTest_Bot):
    """
    Base testing class for message update routers.
    Mock the `handler_send_method` and check the parameters of it
    (Same idea as the `unittest.mock.AsyncMock.assert_called_once_with`).
    """

    input_message_text: str
    handler_send_method: str = "aiogram.types.Message.answer"
    expected_mock_counter: int = 1

    async def setup(self, monkeypatch) -> None:
        if self.update is None:
            self.update = get_update(event=get_message(text=self.input_message_text))
        await super().setup(monkeypatch)


class BaseTest_CallbackUpdate(BaseTest_Bot):
    """
    Base testing class for callback_query update routers.
    Mock the `handler_send_method` and check the parameters of it
    (Same idea as the `unittest.mock.AsyncMock.assert_called_once_with`).
    """

    input_callback_data: str
    handler_send_method: str = "aiogram.types.Message.edit_text"
    expected_mock_counter: int = 2

    async def setup(self, monkeypatch) -> None:
        if self.update is None:
            self.update = get_update(event=get_callback(data=self.input_callback_data))
        await super().setup(monkeypatch)
