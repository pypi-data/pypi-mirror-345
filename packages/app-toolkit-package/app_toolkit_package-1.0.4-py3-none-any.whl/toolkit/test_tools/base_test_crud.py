import pytest
import pytest_asyncio

from ..repo.db import crud
from ..repo.db import exceptions as exc
from ..types_app import _AS, TypeModel
from .base_testdata import Data
from .utils import assert_equal

__all__ = [
    "BaseTest_CRUD",
]

auto_commit_param = pytest.mark.parametrize("auto_commit", (False, True))
filter_data_param = pytest.mark.parametrize(
    "filter_data",
    (
        # all records from table
        lambda x: {},
        # for example: {"color": "red"} - all records with color=red from table
        lambda x: dict([x.data.create_data.copy().popitem()]),
    ),
)


class Message:
    class Error:
        ALREADY_EXISTS = "already exists"
        NOT_FOUND = "not found"


class BaseTest_CRUD:
    data: Data

    # UTILS ==================================================
    async def check_create(self, session: _AS, create_coro, expected_obj) -> None:
        def get_coro():
            return session.get(self.data.model, self.data.uuid)

        assert await get_coro() is None
        assert_equal(await create_coro, expected_obj)
        assert_equal(await get_coro(), expected_obj)

    # FIXTURES =================================================
    @pytest.fixture
    def expected_obj(self) -> TypeModel:
        return self.data.model(**self.data.expected_create)

    @pytest_asyncio.fixture
    async def create_obj(self, get_test_session: _AS, expected_obj) -> TypeModel:
        obj = self.data.get_test_obj()
        get_test_session.add(obj)
        await get_test_session.commit()
        await get_test_session.refresh(obj)
        assert_equal(obj, expected_obj)
        return obj

    # TESTS ========================================================
    # 1. Tests on empty DB:
    @pytest.mark.parametrize("method", ("get_one", "delete", "update"))
    async def test__not_found(self, get_test_session: _AS, method):
        with pytest.raises(exc.NotFound, match=Message.Error.NOT_FOUND):
            await getattr(crud, method)(
                get_test_session,
                self.data.model,
                **(
                    self.data.add_id(**self.data.update_data)
                    if method == "update"
                    else self.data.add_id()
                ),
            )

    @auto_commit_param
    @pytest.mark.parametrize("method", ("insert", "create"))
    async def test__create(
        self, get_test_session: _AS, expected_obj, auto_commit, method
    ):
        def get_coro(invalid: bool = False):
            data = dict(session=get_test_session, commit=auto_commit)
            create_data = (
                self.data.add_id()
                if invalid
                else self.data.add_id(**self.data.create_data)
            )
            return (
                crud.create(obj=self.data.model(**create_data), **data)
                if method == "create"
                else crud.insert(model=self.data.model, **create_data, **data)
            )

        with pytest.raises(
            expected_exception=exc.NotNullViolationError,
            match="null value in column ",
        ):
            await get_coro(invalid=True)
        await get_test_session.rollback()

        await self.check_create(
            session=get_test_session,
            expected_obj=expected_obj,
            create_coro=get_coro(),
        )
        with pytest.raises(
            expected_exception=exc.AlreadyExists,
            match=Message.Error.ALREADY_EXISTS,
        ):
            await get_coro()

    @filter_data_param
    async def test__get_all_empty(self, get_test_session: _AS, filter_data):
        assert_equal(
            expected=[],
            actual=await crud.get_all(
                session=get_test_session,
                model=self.data.model,
                **filter_data(self),
            ),
        )

    # 2. Tests on filled with one record DB (used fixture create_obj):
    @filter_data_param
    async def test__get_all(
        self, create_obj, get_test_session: _AS, expected_obj, filter_data
    ):
        assert_equal(
            expected=[expected_obj],
            actual=await crud.get_all(
                session=get_test_session,
                model=self.data.model,
                **filter_data(self),
            ),
        )

    async def test__get_one(self, create_obj, get_test_session: _AS, expected_obj):
        assert_equal(
            expected=expected_obj,
            actual=await crud.get_one(
                session=get_test_session,
                model=self.data.model,
                id=create_obj.id,
            ),
        )

    @auto_commit_param
    async def test__delete(
        self, create_obj, get_test_session: _AS, expected_obj, auto_commit
    ):
        def get_coro():
            return crud.delete(
                session=get_test_session,
                model=self.data.model,
                id=create_obj.id,
                commit=auto_commit,
            )

        assert_equal(
            expected=expected_obj,
            actual=await get_coro(),
        )
        with pytest.raises(exc.NotFound, match=Message.Error.NOT_FOUND):
            await get_coro()

    @auto_commit_param
    async def test__update(self, create_obj, get_test_session: _AS, auto_commit):
        assert_equal(
            expected=self.data.model(**self.data.expected_update),
            actual=await crud.update(
                session=get_test_session,
                model=self.data.model,
                id=create_obj.id,
                commit=auto_commit,
                **self.data.update_data,
            ),
        )
