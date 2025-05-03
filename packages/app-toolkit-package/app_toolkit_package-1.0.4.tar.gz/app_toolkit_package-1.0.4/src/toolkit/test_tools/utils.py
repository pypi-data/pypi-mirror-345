import inspect
from importlib import import_module
from pprint import pprint
from typing import Any

import pytest

from ..types_app import _F

__all__ = [
    "assert_equal",
    "assert_isinstance",
    "info",
    "find_in_stack",
    "mock",
]

SEP_LENGTH = 10
SEP = f"\n{'=' * SEP_LENGTH}\n"
ERR_MSG = "".join(
    (
        SEP,
        "ACTUAL:\n{actual}",
        SEP,
        "EXPECTED:\n{expected}",
        SEP,
    )
)


# def assert_equal(
#     actual: Any,
#     expected: Any,
#     func: _F | None = None,
#     exclude: list[str] | None = None,
# ) -> None:
#     """
#     Simple helper comparing two entities.
#     `func` is a helper function applied to both entities,
#     usually it is `set` for sequences for unordered comparison.
#     ```
#     if func is not None:
#         actual, expected = map(func, (actual, expected))
#     assert actual == expected, (actual, expected)
#     ```
#     """
#     if func is not None:
#         actual, expected = map(func, (actual, expected))
#     if exclude is not None:
#         actual = actual.copy()
#         expected = expected.copy()
#         for exc in exclude:
#             for entity in (actual, expected):
#                 if isinstance(entity, dict):
#                     entity.pop(exc)
#                 elif isinstance(entity, (list, set)):
#                     entity.remove(exc)
#     assert actual == expected,
# ERR_MSG.format(actual=actual, expected=expected)


def assert_equal(
    actual: Any,
    expected: Any,
    func: _F | None = None,
    exclude: list[str] | None = None,
) -> None:
    """
    Simple helper comparing two entities.
    `func` is a helper function applied to both entities,
    usually it is `set` for sequences for unordered comparison.
    ```
    if func is not None:
        actual, expected = map(func, (actual, expected))
    assert actual == expected, (actual, expected)
    ```
    """
    MutSeq = (list, set)
    MutType = (dict, *MutSeq)

    def _copy(item):
        return item.copy() if isinstance(item, MutType) else item

    def _list(item):
        return item if isinstance(item, MutSeq) else [item]

    actual, expected = map(_copy, (actual, expected))

    if func is not None:
        actual, expected = map(func, (actual, expected))

    if exclude is not None:
        # Convert to list if it already is not
        actual, expected = map(_list, (actual, expected))

        for a, e in zip(actual, expected):
            for exc in exclude:
                for entity in (a, e):
                    if isinstance(entity, dict):
                        entity.pop(exc)
                    elif isinstance(entity, MutSeq):
                        entity.remove(exc)
    assert actual == expected, ERR_MSG.format(actual=actual, expected=expected)


def assert_isinstance(obj, cls) -> None:
    assert isinstance(obj, cls), ERR_MSG.format(actual=type(obj), expected=cls)


def info(*items, raising: bool = True):
    for item in items:
        pprint(item)
    if raising:
        assert 0


def find_in_stack(name: str, level: int = 7) -> None:
    for i in range(level):
        if inspect.stack()[i][3] == name:
            return None
    assert 0, f"Cannot find the entity name `{name}` in the stack."


def mock(
    monkeypatch: pytest.MonkeyPatch,
    module: object | str,
    func: _F | str,
    mock_func: _F | object,
) -> None:
    func_name = func if isinstance(func, str) else func.__name__
    if isinstance(module, str):
        module = import_module(module)
    assert hasattr(module, func_name), (
        f"Module `{module!r}` has no method `{func_name}`."
    )
    monkeypatch.setattr(module, func_name, mock_func)
