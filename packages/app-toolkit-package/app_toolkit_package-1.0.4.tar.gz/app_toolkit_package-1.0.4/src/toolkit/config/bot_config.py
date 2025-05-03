from pydantic import PositiveInt, SecretStr

from .base import BaseConf, SettingsConfigDict

TEST_TOKEN = f"{'0' * 8}:{'a' * 17}-{'b' * 3}_{'c' * 13}"
# https://stackoverflow.com/questions/61868770/tegram-bot-api-token-format
# regex = /^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$/


class SettingsBot(BaseConf):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    emoji: bool = True
    token: SecretStr = TEST_TOKEN
    name_max_length: PositiveInt = 50
    description_max_length: PositiveInt = 500


bot_conf = SettingsBot()
