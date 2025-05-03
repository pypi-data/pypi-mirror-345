from datetime import datetime, timedelta, timezone

import jwt
from pydantic import ValidationError

from ...models.user import BaseUser as User
from ..api.exceptions import ExpiredToken, InvalidTokenPayload
from ..config import auth_conf
from ..schemas import TokenPayload


def create_access_token(
    user: User,
    expires_delta=timedelta(minutes=auth_conf.TOKEN_LIFETIME),
) -> str:
    return jwt.encode(
        key=auth_conf.SECRET_KEY.get_secret_value(),
        algorithm=auth_conf.ALGORITHM,
        payload=TokenPayload(
            sub=user.email,
            exp=datetime.now(timezone.utc) + expires_delta,
        ).model_dump(),
    )


def get_token_payload(token: str) -> TokenPayload | None:
    try:
        payload = TokenPayload.model_validate(
            obj=jwt.decode(
                jwt=token,
                key=auth_conf.SECRET_KEY.get_secret_value(),
                algorithms=[auth_conf.ALGORITHM],
            )
        )
    except (jwt.exceptions.PyJWTError, ValidationError):
        raise InvalidTokenPayload
    if payload.exp < datetime.now(timezone.utc):
        raise ExpiredToken
    return payload
