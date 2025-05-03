from pydantic import EmailStr, PositiveInt, SecretStr

from .base import BaseConf


class SettingsApp(BaseConf):
    # Below settings are mostly for FastAPI/FastAPI_Users
    DEFAULT_STR: str = "To be implemented in .env file"
    url_prefix: str = "/api/v1"
    app_title: str = f"App title: {DEFAULT_STR}"
    app_description: str = f"App description: {DEFAULT_STR}"
    secret_key: SecretStr = f"Secret key {DEFAULT_STR}"

    # Endpoint access settings
    SUPER_ONLY: str = "__Только для суперюзеров:__ "
    AUTH_ONLY: str = "__Только для авторизованных пользователей:__ "
    ALL_USERS: str = "__Для всех пользователей:__ "

    # Authentication settings
    admin_email: EmailStr = "adm@adm.com"
    admin_password: SecretStr = "adm"
    password_length: PositiveInt = 3
    auth_backend_name: str = "jwt"
    token_url: str = "auth/jwt/login"
    token_lifetime: PositiveInt = 3600


app_conf = SettingsApp()
