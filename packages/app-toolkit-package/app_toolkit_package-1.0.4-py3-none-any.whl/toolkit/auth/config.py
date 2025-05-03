from pydantic import EmailStr, PositiveInt, SecretStr

from ..config import base
from ..types_app import NonEmptyStr


class SettingsAuth(base.BaseConf):
    TOKEN_URL: NonEmptyStr = "/auth/jwt/login"
    TOKEN_LIFETIME: PositiveInt = 3600
    SECRET_KEY: SecretStr = (
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    ALGORITHM: NonEmptyStr = "HS256"

    # Endpoint access settings
    SUPER_ONLY: NonEmptyStr = "__Только для суперюзеров:__ "
    AUTH_ONLY: NonEmptyStr = "__Только для авторизованных пользователей:__ "
    ALL_USERS: NonEmptyStr = "__Для всех пользователей:__ "

    # Authentication settings
    EMAIL: EmailStr = "admin@admin.com"
    PASSWORD: SecretStr = "admin_pwd"
    FIRST_NAME: str = "admin"
    LAST_NAME: str = "admin"
    PHONE_NUMBER: str = "+79991112233"


auth_conf = SettingsAuth()
