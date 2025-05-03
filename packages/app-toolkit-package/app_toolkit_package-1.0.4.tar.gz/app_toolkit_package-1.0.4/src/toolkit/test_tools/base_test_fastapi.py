from enum import Enum
from typing import TypeAlias

from fastapi import APIRouter
from httpx import AsyncClient, Response

from ..auth import schemas
from ..auth.api.endpoints import login_user
from ..types_app import _AS, _F, Any, TypeResponseJson
from ..utils.converter import jsonable_converter
from .mixins import check_db, setup_db
from .utils import assert_equal

__all__ = [
    "request",
    "API_Router",
    "BaseTest_API",
    "HTTPMethod",
    "TypeHTTPMethod",
]


class API_Router:
    router: APIRouter


class HTTPMethod(Enum):
    DELETE, GET, PATCH, POST, PUT = range(5)

    @classmethod
    def get_member_names(cls):
        return map(str.lower, cls._member_names_)


TypeResponseModel: TypeAlias = Any | None
TypeHeader: TypeAlias = dict[str, str] | None
TypeHTTPMethod: TypeAlias = HTTPMethod | str


def reverse(
    *,
    router: APIRouter | None = None,
    path_func: _F,
    **path_params,
) -> str:
    if router is None:
        router = API_Router.router
    return router.url_path_for(path_func.__name__, **path_params)


def get_http_method(http_method: TypeHTTPMethod) -> str:
    if isinstance(http_method, HTTPMethod):
        http_method = http_method.name.lower()
    elif isinstance(http_method, str):
        http_method = http_method.lower()
    else:
        raise ValueError(f"Invalid HTTP method type {type(http_method)}")
    if http_method not in HTTPMethod.get_member_names():
        raise ValueError(f"Invalid HTTP method {http_method}")
    return http_method


def check_response(
    *,
    response: Response,
    expected_status_code: int = 200,
    expected_response_json: TypeResponseJson = None,
    expected_response_json_exclude: list[str] | None = None,
    expected_response_model: TypeResponseModel = None,
    expected_response_headers: TypeHeader = None,
) -> Response:
    resp_json = response.json()
    assert response.status_code == expected_status_code, (
        response.status_code,
        resp_json,
    )
    if expected_response_headers is not None:
        for k, v in expected_response_headers.items():
            assert_equal(response.headers.get(k), v)
    if expected_response_model is not None:
        expected_response_model.model_validate(resp_json)
    if expected_response_json is not None:
        assert_equal(
            actual=resp_json,
            expected=expected_response_json,
            exclude=expected_response_json_exclude,
        )
    return response


def get_param(param_name: str, param: Any):
    return {param_name: param} if param is not None else {}


async def request(
    async_client: AsyncClient,
    *,
    router: APIRouter | None = None,
    http_method: TypeHTTPMethod,
    path_func: _F,
    expected_status_code: int = 200,
    expected_response_json: TypeResponseJson = None,
    expected_response_json_exclude: list[str] | None = None,
    expected_response_model: TypeResponseModel = None,
    expected_response_headers: TypeHeader = None,
    headers: TypeHeader = None,
    query_params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    **path_params,
) -> Response:
    return check_response(
        expected_status_code=expected_status_code,
        expected_response_json=expected_response_json,
        expected_response_json_exclude=expected_response_json_exclude,
        expected_response_model=expected_response_model,
        expected_response_headers=expected_response_headers,
        response=await getattr(async_client, get_http_method(http_method))(
            url=reverse(router=router, path_func=path_func, **path_params),
            params=query_params,
            **get_param("headers", headers),
            **get_param("data", data),
            **get_param("json", json),
            # **(dict(headers=headers) if headers is not None else {}),
            # **(dict(data=data) if data is not None else {}),
            # **(dict(json=json) if json is not None else {}),
        ),
    )


async def get_header(client: AsyncClient, login_data: dict[str, Any]):
    t = schemas.Token.model_validate(
        obj=(
            await client.post(
                url=reverse(path_func=login_user),
                data=schemas.UserLoginForm(**login_data).model_dump(),
            )
        ).json()
    )
    return {"Authorization": f"Bearer {t.access_token}"}


class BaseTest_API:
    router: APIRouter | None = None
    http_method: TypeHTTPMethod
    path_func: _F  # type: ignore [valid-type]
    path_params: dict[str, Any] = {}
    query_params: dict[str, Any] | None = None
    form_data: dict[str, Any] | None = None
    json: dict[str, Any] | None = None
    expected_status_code: int = 200
    expected_response_model: TypeResponseModel = None
    expected_response_headers: TypeHeader = None
    expected_response_json: TypeResponseJson = None
    expected_response_json_exclude: list[str] | None = None
    login_data: dict[str, Any] | None = None

    async def test__endpoint(
        self, async_client: AsyncClient, get_test_session: _AS
    ) -> None:
        await setup_db(self, get_test_session)
        response = await request(
            async_client,
            router=self.router,
            http_method=self.http_method,
            path_func=self.path_func,
            **self.path_params,
            query_params=self.query_params,
            data=self.form_data,
            json=jsonable_converter(self.json),  # type: ignore [arg-type]
            headers=(
                await get_header(async_client, self.login_data)
                if self.login_data is not None
                else None
            ),
            expected_status_code=self.expected_status_code,
            expected_response_json=self.expected_response_json,
            expected_response_json_exclude=self.expected_response_json_exclude,
            expected_response_model=self.expected_response_model,
            expected_response_headers=self.expected_response_headers,
        )
        await check_db(self, get_test_session, response)
