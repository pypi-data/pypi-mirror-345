from datetime import datetime

from pydantic import BaseModel, EmailStr

from ..types_app import NonEmptyStr


class UserLoginForm(BaseModel):
    username: EmailStr
    password: NonEmptyStr


class Token(BaseModel):
    # The fields are mandatory as per OAuth2 spec
    access_token: NonEmptyStr
    token_type: NonEmptyStr = "bearer"


class TokenPayload(BaseModel):
    exp: datetime
    sub: EmailStr
