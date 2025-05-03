from functools import partial
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError

from ..models.base import Base
from ..types_app import _AS, TypeModel
from .base_testdata import Data
from .utils import assert_equal, assert_isinstance

__all__ = [
    "BaseTest_Model",
]


class BaseTest_Model:
    data: Data

    # UTILS ==================================================
    def get_fields(self, *filter_data) -> list:
        return [
            c
            for f in filter_data
            for c in self.data.model.__table__.c
            if getattr(c, f, None)
        ]

    def get_field_names(
        self, *filter_data, exclude: list[str] | None = None
    ) -> list[str]:
        return [
            c.name
            for c in self.get_fields(*filter_data)
            if c.name not in self.data.get_val_or_sub(exclude, [])
        ]

    def get_fields_asdict(
        self, filter: str, exclude: list[str] | None = None
    ) -> dict[str, Any]:
        return {
            c.name: getattr(c, filter).arg
            for c in self.get_fields(filter)
            if c.name not in self.data.get_val_or_sub(exclude, [])
        }

    # FIXTURES =================================================
    @pytest.fixture
    def obj(self) -> TypeModel:
        """Instance of model class(**create_data) used for methods testing."""
        return self.data.model(**self.data.create_data)

    # TESTS ========================================================
    def test__model(self):
        assert issubclass(self.data.model, Base), type(self.data.model)

    # Fields
    def test__fields(self):
        assert_equal_set = partial(assert_equal, func=set)
        assert_equal_set(
            expected=self.data.pk_fields,
            actual=self.get_field_names("primary_key"),
        )
        assert_equal_set(
            expected=self.data.unique_fields,
            actual=self.get_field_names("unique"),
        )
        assert_equal_set(
            expected=self.data.indexed_fields,
            actual=self.get_field_names("index"),
        )
        assert_equal_set(
            expected=self.data.nullable_fields,
            actual=self.get_field_names("nullable"),
        )
        assert "id" in self.get_fields_asdict("default")
        assert_equal(
            expected=self.data.default_data,
            actual=self.get_fields_asdict("default", exclude=["id"]),
        )

    async def test__required_fields(self, get_test_session: _AS):
        """Testing model required fields cannot be NULL."""
        err_msg = 'null value in column "{column}" of relation "{relation}" violates not-null constraint'
        passed = []
        for field in self.data.create_data:
            obj = self.data.model(**{**self.data.create_data, **{field: None}})
            get_test_session.add(obj)
            with pytest.raises(
                expected_exception=IntegrityError,
                match=err_msg.format(
                    column=field, relation=self.data.model.__tablename__
                ),
            ):
                passed.append(field)
                await get_test_session.commit()
            await get_test_session.rollback()
        assert_equal(passed, list(self.data.create_data))

    # Methods
    def test__model_dump(self, obj: TypeModel):
        """Testing `model_dump()` method and `exclude=` argument."""
        assert_equal(obj.model_dump(), self.data.dump_initial)  # type: ignore [call-arg]
        assert_equal(obj.model_dump(*self.data.dump_initial), {})  # type: ignore [call-arg]

    def test__eq(self, obj: TypeModel):
        other_obj = self.data.model(**self.data.create_data)
        assert id(other_obj) != id(obj)
        assert_equal(other_obj.model_dump(), obj.model_dump())  # type: ignore [call-arg]
        assert_equal(other_obj, obj)
        other_obj.id = 1
        assert other_obj != obj

    def test__repr(self, obj: TypeModel):
        globals, locals = None, {f"{self.data.model.__name__}": self.data.model}
        other_obj = eval(repr(obj), globals, locals)
        assert_isinstance(other_obj, type(obj))
        assert id(other_obj) != id(obj)
        assert_equal(other_obj, obj)
