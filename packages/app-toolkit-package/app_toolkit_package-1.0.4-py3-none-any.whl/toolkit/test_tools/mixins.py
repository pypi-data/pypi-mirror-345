from typing import Any

from httpx import Response

from ..api.fastapi import utils
from ..models.base import Base
from ..types_app import _AS, _F
from ..utils.converter import jsonable_converter
from .utils import assert_equal, assert_isinstance

__all__ = [
    "ClientNoCacheMixin",
    "PathParamsMixin",
    "NotFoundMixin",
    "DBMixin",
    "check_db",
    "setup_db",
]


class ClientNoCacheMixin:
    expected_response_headers: dict[str, str] = utils.CLIENT_NO_CACHE


class PathParamsMixin:
    path_params: dict[str, Any]


class NotFoundMixin:
    expected_status_code: int = 404
    expected_response_json: dict[str, Any] | None


class DBMixin:
    db_save_obj: _F | None = None  # type: ignore [valid-type]
    db_vs_response: bool = False
    db_vs_response_exclude: list[str] | None = None
    db_delete_action: bool = False
    model = None
    """
    Model is necessary for:
        * obj creation checking - needs model
        * obj deletion checking - derives from db_save_obj
        * obj update checking - derives from db_save_obj
    """

    async def setup_db(self, session: _AS) -> None:
        if self.db_save_obj is not None:
            self.obj = self.db_save_obj()
            session.add(self.obj)
            await session.commit()
            if self.model is None:
                self.model = self.obj.__class__

    async def check_db(self, session: _AS, response: Response) -> None:
        assert_isinstance(response, Response)
        if self.db_vs_response:
            if self.model is None:
                raise NotImplementedError("No model for DB checking.")
            from_db = await session.get(self.model, response.json().get("id"))
            if self.db_delete_action:
                assert from_db is None
            else:
                assert from_db is not None
                assert_isinstance(from_db, Base)
                await session.refresh(from_db)
                response_json: dict = response.json()
                if self.db_vs_response_exclude is not None:
                    for item in self.db_vs_response_exclude:
                        response_json.pop(item, None)
                assert_equal(
                    expected=response_json,
                    actual=jsonable_converter(
                        from_db.model_dump(*self.db_vs_response_exclude or [])
                    ),
                )


async def setup_db(obj, session: _AS):
    if hasattr(obj, "setup_db"):
        await obj.setup_db(session)


async def check_db(obj, session: _AS, response: Response):
    if hasattr(obj, "check_db"):
        await obj.check_db(session, response)
