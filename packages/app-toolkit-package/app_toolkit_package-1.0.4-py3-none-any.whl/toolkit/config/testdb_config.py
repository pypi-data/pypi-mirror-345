from sqlalchemy.pool import NullPool

from .db_config import SettingsConfigDict, SettingsDB


class SettingsTestDB(SettingsDB):
    model_config = SettingsConfigDict(env_prefix="TEST_DB_")


db_conf = SettingsTestDB()
engine, async_session, get_async_session = db_conf.get_dependencies(
    poolclass=NullPool,
    # expire_on_commit=False,
    # autoflush=False,
)


# assert_equal(
#     str(db_conf.DATABASE_URI),
#     "postgresql+asyncpg://postgres_test_user:postgres_test_pwd@postgres_test_host:5432/postgres_test_name",
#     # == "postgresql+asyncpg://github_actions:github_actions@0.0.0.0:5432/github_actions"
# )
