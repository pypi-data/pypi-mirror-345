from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConf(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore"
    )
