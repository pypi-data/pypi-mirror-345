from ...api.fastapi.dependencies import async_session
from ...repo.db import crud, exceptions
from ..api.dependencies import jwt_token, login_form_data
from ..api.exceptions import IncorrectLoginCredentials, InvalidTokenPayload
from .password import verify_password
from .token import get_token_payload


async def authenticate_user(
    session: async_session,
    data: login_form_data,
):
    from src.models import User

    try:
        user: User = await crud.get_one(
            session,
            User,
            email=data.username,
        )
    except exceptions.NotFound:
        raise IncorrectLoginCredentials
    if not verify_password(data.password, user.password):
        raise IncorrectLoginCredentials
    return user


async def get_current_user(
    session: async_session,
    token: jwt_token,
):
    from src.models import User

    try:
        return await crud.get_one(
            session,
            User,
            email=get_token_payload(token).sub,  # type: ignore [union-attr]
        )
    except exceptions.NotFound:
        raise InvalidTokenPayload
